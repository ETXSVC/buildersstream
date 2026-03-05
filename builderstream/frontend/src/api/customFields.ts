import { apiClient } from './client';

export type FieldType =
  | 'text'
  | 'textarea'
  | 'number'
  | 'date'
  | 'boolean'
  | 'select'
  | 'multi_select'
  | 'url'
  | 'email'
  | 'phone';

export type ModelName =
  | 'project'
  | 'lead'
  | 'contact'
  | 'company'
  | 'invoice'
  | 'estimate'
  | 'proposal'
  | 'service_ticket'
  | 'inspection'
  | 'daily_log';

export interface CustomFieldDefinition {
  id: string;
  model_name: ModelName;
  name: string;
  label: string;
  field_type: FieldType;
  options: string[];
  required: boolean;
  default_value: unknown;
  placeholder: string;
  help_text_field: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type CustomFieldDefinitionCreate = Omit<
  CustomFieldDefinition,
  'id' | 'created_at' | 'updated_at'
>;

export async function fetchCustomFieldDefinitions(
  params?: { model_name?: ModelName; is_active?: boolean },
): Promise<{ results: CustomFieldDefinition[]; count: number }> {
  const { data } = await apiClient.get('/api/v1/custom-fields/definitions/', { params });
  return data;
}

export async function fetchFieldsForModel(
  modelName: ModelName,
): Promise<CustomFieldDefinition[]> {
  const { data } = await apiClient.get(
    `/api/v1/custom-fields/definitions/for-model/${modelName}/`,
  );
  return data;
}

export async function createCustomFieldDefinition(
  payload: Partial<CustomFieldDefinitionCreate>,
): Promise<CustomFieldDefinition> {
  const { data } = await apiClient.post('/api/v1/custom-fields/definitions/', payload);
  return data;
}

export async function updateCustomFieldDefinition(
  id: string,
  payload: Partial<CustomFieldDefinitionCreate>,
): Promise<CustomFieldDefinition> {
  const { data } = await apiClient.patch(
    `/api/v1/custom-fields/definitions/${id}/`,
    payload,
  );
  return data;
}

export async function deleteCustomFieldDefinition(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/custom-fields/definitions/${id}/`);
}
