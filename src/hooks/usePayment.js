import { useState } from 'react';
import paymentService from '../services/paymentService';

export const usePayment = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const processPayment = async (projectId, paymentData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.processPayment(projectId, paymentData);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const verifyPayment = async (paymentId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.verifyPayment(paymentId);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getPaymentStatus = async (paymentId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.getPaymentStatus(paymentId);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getPaymentHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.getPaymentHistory();
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const refundPayment = async (paymentId, reason) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.refundPayment(paymentId, reason);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const calculateProjectPrice = async (projectId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.calculateProjectPrice(projectId);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const validateDiscount = async (discountCode, projectId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.validateDiscount(discountCode, projectId);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getPaymentMethods = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.getPaymentMethods();
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const addPaymentMethod = async (methodData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.addPaymentMethod(methodData);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deletePaymentMethod = async (methodId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await paymentService.deletePaymentMethod(methodId);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  return {
    loading,
    error,
    processPayment,
    verifyPayment,
    getPaymentStatus,
    getPaymentHistory,
    refundPayment,
    calculateProjectPrice,
    validateDiscount,
    getPaymentMethods,
    addPaymentMethod,
    deletePaymentMethod,
    clearError
  };
};

export default usePayment;
