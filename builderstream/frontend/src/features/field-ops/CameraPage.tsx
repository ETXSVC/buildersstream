import { MobilePhotoCapture } from '@/components/mobile/MobilePhotoCapture';
import { MobileExpenseCapture } from '@/components/mobile/MobileExpenseCapture';

export const CameraPage = () => {
  return (
    <div className="p-4">
      <h1 className="mb-1 text-xl font-bold text-slate-900">Capture</h1>
      <p className="mb-6 text-sm text-slate-500">Photos and receipts</p>
      <MobilePhotoCapture />
      <div className="mt-8 border-t border-slate-200 pt-6">
        <h2 className="mb-4 text-base font-semibold text-slate-800">Expense Receipt</h2>
        <MobileExpenseCapture />
      </div>
    </div>
  );
};
