import { QualityResult, DetectionResult } from '../types/inspection';
import { api } from './api';

class InspectionService {
  async checkImageQuality(file: File): Promise<QualityResult> {
    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await api.post('/inspection/quality', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error('Error checking image quality:', error);
      throw new Error('Failed to check image quality');
    }
  }

  async detectDamages(file: File): Promise<DetectionResult> {
    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await api.post('/inspection/detect', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      console.error('Error detecting damages:', error);
      throw new Error('Failed to detect damages');
    }
  }
}

export const inspectionService = new InspectionService();