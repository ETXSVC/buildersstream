/**
 * GeofenceService — checks whether the user's current GPS position is within
 * the configured radius of a job site before allowing clock-in.
 * Uses the Haversine formula for distance calculation.
 * Caches job site coordinates in IndexedDB via offlineDb.
 */

import { offlineDb, CachedProject } from './offlineDb';

export type GeolocationResult = {
  latitude: number;
  longitude: number;
  accuracy: number;
};

export type GeofenceCheckResult = {
  isWithin: boolean;
  distanceMeters: number;
  radiusMeters: number;
  position: GeolocationResult;
};

function haversineMeters(
  lat1: number, lon1: number,
  lat2: number, lon2: number
): number {
  const R = 6_371_000; // Earth radius in metres
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export const geofenceService = {
  /**
   * Get current GPS position from the browser.
   * Throws if permission denied or unavailable.
   */
  getCurrentPosition(): Promise<GeolocationResult> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }
      navigator.geolocation.getCurrentPosition(
        (pos) =>
          resolve({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
          }),
        (err) => reject(new Error(err.message)),
        { enableHighAccuracy: true, timeout: 10_000, maximumAge: 30_000 }
      );
    });
  },

  /**
   * Check whether the user is within the project's geofence radius.
   * Falls back to allowing clock-in if the project has no coordinates configured.
   */
  async checkGeofence(projectId: string): Promise<GeofenceCheckResult> {
    const position = await geofenceService.getCurrentPosition();
    const project = await offlineDb.getProject(projectId);

    if (!project?.latitude || !project?.longitude) {
      return {
        isWithin: true,
        distanceMeters: 0,
        radiusMeters: 0,
        position,
      };
    }

    const radiusMeters = project.geofenceRadius ?? 300;
    const distanceMeters = haversineMeters(
      position.latitude, position.longitude,
      project.latitude, project.longitude
    );

    return {
      isWithin: distanceMeters <= radiusMeters,
      distanceMeters,
      radiusMeters,
      position,
    };
  },

  /**
   * Cache project coordinates from API response into IndexedDB.
   */
  async cacheProjectCoordinates(projects: CachedProject[]): Promise<void> {
    await offlineDb.cacheProjects(projects);
  },
};
