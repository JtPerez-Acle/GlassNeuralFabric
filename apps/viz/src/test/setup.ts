// Test setup file for Vitest
import '@testing-library/jest-dom';

// Mock ResizeObserver which isn't available in jsdom
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
