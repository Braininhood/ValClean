/**
 * API Endpoints Configuration
 * 
 * All endpoints use security prefixes as documented in VALCLEAN_BEST_SOLUTION.md
 */

// Public Endpoints (No authentication required)
export const PUBLIC_ENDPOINTS = {
  // Services (Security: /api/svc/)
  SERVICES: {
    LIST: '/svc/',
    DETAIL: (id: string | number) => `/svc/${id}/`,
    BY_POSTCODE: '/svc/by-postcode/',
  },
  
  // Staff (Public listing) (Security: /api/stf/)
  STAFF: {
    LIST: '/stf/',
    BY_POSTCODE: '/stf/by-postcode/',
    DETAIL: (id: string | number) => `/stf/${id}/`,
  },
  
  // Bookings/Orders (Security: /api/bkg/)
  BOOKINGS: {
    CREATE: '/bkg/',
    SUBSCRIPTION: '/bkg/subscription/',
    ORDER: '/bkg/order/',
    CANCEL: (id: string | number) => `/bkg/${id}/cancel/`,
    
    // Guest order access (NO AUTH REQUIRED)
    GUEST_ORDER: (orderNumber: string) => `/bkg/guest/order/${orderNumber}/`,
    GUEST_ORDER_VERIFY: (orderNumber: string) => `/bkg/guest/order/${orderNumber}/verify/`,
    GUEST_ORDER_TRACK: (token: string) => `/bkg/guest/order/track/${token}/`,
    GUEST_ORDER_CANCEL: (orderNumber: string) => `/bkg/guest/order/${orderNumber}/cancel/`,
    GUEST_ORDER_REQUEST_CHANGE: (orderNumber: string) => `/bkg/guest/order/${orderNumber}/request-change/`,
    GUEST_ORDER_LINK_LOGIN: (orderNumber: string) => `/bkg/guest/order/${orderNumber}/link-login/`,
    GUEST_ORDER_LINK_REGISTER: (orderNumber: string) => `/bkg/guest/order/${orderNumber}/link-register/`,
    
    // Guest subscription access (NO AUTH REQUIRED)
    GUEST_SUBSCRIPTION: (subscriptionNumber: string) => `/bkg/guest/subscription/${subscriptionNumber}/`,
    GUEST_SUBSCRIPTION_VERIFY: (subscriptionNumber: string) => `/bkg/guest/subscription/${subscriptionNumber}/verify/`,
    GUEST_SUBSCRIPTION_TRACK: (token: string) => `/bkg/guest/subscription/track/${token}/`,
    GUEST_SUBSCRIPTION_PAUSE: (subscriptionNumber: string) => `/bkg/guest/subscription/${subscriptionNumber}/pause/`,
    GUEST_SUBSCRIPTION_CANCEL: (subscriptionNumber: string) => `/bkg/guest/subscription/${subscriptionNumber}/cancel/`,
    GUEST_SUBSCRIPTION_APPOINTMENT_CANCEL: (subscriptionNumber: string, apptId: string | number) => 
      `/bkg/guest/subscription/${subscriptionNumber}/appointments/${apptId}/cancel/`,
    GUEST_SUBSCRIPTION_LINK_LOGIN: (subscriptionNumber: string) => `/bkg/guest/subscription/${subscriptionNumber}/link-login/`,
    GUEST_SUBSCRIPTION_LINK_REGISTER: (subscriptionNumber: string) => `/bkg/guest/subscription/${subscriptionNumber}/link-register/`,
    
    // Account linking check
    GUEST_CHECK_EMAIL: '/bkg/guest/check-email/',
  },
  
  // Address (Security: /api/addr/)
  ADDRESS: {
    AUTOCOMPLETE: '/addr/autocomplete/',
    VALIDATE: '/addr/validate/',
  },
  
  // Authentication (Security: /api/aut/)
  AUTH: {
    LOGIN: '/aut/login/',
    REGISTER: '/aut/register/',
    LOGOUT: '/aut/logout/',
    REFRESH: '/aut/refresh/',
    PASSWORD_RESET: '/aut/password-reset/',
    CHECK_EMAIL: '/aut/check-email/',
  },
  
  // Available Slots (Security: /api/slots/)
  SLOTS: {
    LIST: '/slots/',
  },
  
  // Payments (Security: /api/pay/)
  PAYMENTS: {
    CREATE_INTENT: '/pay/create-intent/',
    CONFIRM: '/pay/confirm/',
    WEBHOOK: '/pay/webhook/',
  },
};

// Protected Endpoints (Authentication required)

// Customer Endpoints (Security: /api/cus/)
export const CUSTOMER_ENDPOINTS = {
  APPOINTMENTS: {
    LIST: '/cus/appointments/',
    DETAIL: (id: string | number) => `/cus/appointments/${id}/`,
    CANCEL: (id: string | number) => `/cus/appointments/${id}/cancel/`,
    RESCHEDULE: (id: string | number) => `/cus/appointments/${id}/reschedule/`,
  },
  
  SUBSCRIPTIONS: {
    LIST: '/cus/subscriptions/',
    CREATE: '/cus/subscriptions/',
    DETAIL: (id: string | number) => `/cus/subscriptions/${id}/`,
    UPDATE: (id: string | number) => `/cus/subscriptions/${id}/`,
    PAUSE: (id: string | number) => `/cus/subscriptions/${id}/pause/`,
    CANCEL: (id: string | number) => `/cus/subscriptions/${id}/cancel/`,
    APPOINTMENT_CANCEL: (id: string | number, apptId: string | number) => 
      `/cus/subscriptions/${id}/appointments/${apptId}/cancel/`,
  },
  
  ORDERS: {
    LIST: '/cus/orders/',
    CREATE: '/cus/orders/',
    DETAIL: (id: string | number) => `/cus/orders/${id}/`,
    REQUEST_CHANGE: (id: string | number) => `/cus/orders/${id}/request-change/`,
    CANCEL: (id: string | number) => `/cus/orders/${id}/cancel/`,
    STATUS: (id: string | number) => `/cus/orders/${id}/status/`,
  },
  
  PROFILE: {
    GET: '/cus/profile/',
    UPDATE: '/cus/profile/',
  },
  
  INVOICES: {
    LIST: '/cus/invoices/',
  },
  
  CALENDAR: {
    CONNECT: '/cus/calendar/connect/',
    STATUS: '/cus/calendar/status/',
    SYNC: '/cus/calendar/sync/',
    DISCONNECT: '/cus/calendar/disconnect/',
    EVENTS: '/cus/calendar/events/',
    ADD_EVENT: '/cus/calendar/add-event/',
  },
};

// Staff Endpoints (Security: /api/st/)
export const STAFF_ENDPOINTS = {
  SCHEDULE: '/st/schedule/',
  JOBS: {
    LIST: '/st/jobs/',
    CHECKIN: (id: string | number) => `/st/jobs/${id}/checkin/`,
    COMPLETE: (id: string | number) => `/st/jobs/${id}/complete/`,
  },
  AVAILABILITY: {
    GET: '/st/availability/',
    UPDATE: '/st/availability/',
  },
  CALENDAR: {
    CONNECT: '/st/calendar/connect/',
    STATUS: '/st/calendar/status/',
    SYNC: '/st/calendar/sync/',
    DISCONNECT: '/st/calendar/disconnect/',
    EVENTS: '/st/calendar/events/',
    ADD_EVENT: '/st/calendar/add-event/',
  },
};

// Manager Endpoints (Security: /api/man/)
export const MANAGER_ENDPOINTS = {
  APPOINTMENTS: {
    LIST: '/man/appointments/',
    CREATE: '/man/appointments/',
    UPDATE: (id: string | number) => `/man/appointments/${id}/`,
    DELETE: (id: string | number) => `/man/appointments/${id}/`,
  },
  STAFF: {
    LIST: '/man/staff/',
    UPDATE: (id: string | number) => `/man/staff/${id}/`,
  },
  CUSTOMERS: {
    LIST: '/man/customers/',
    DETAIL: (id: string | number) => `/man/customers/${id}/`,
    UPDATE: (id: string | number) => `/man/customers/${id}/`,
  },
  REPORTS: {
    REVENUE: '/man/reports/revenue/',
    APPOINTMENTS: '/man/reports/appointments/',
  },
  CALENDAR: {
    CONNECT: '/man/calendar/connect/',
    STATUS: '/man/calendar/status/',
    SYNC: '/man/calendar/sync/',
    DISCONNECT: '/man/calendar/disconnect/',
    EVENTS: '/man/calendar/events/',
    ADD_EVENT: '/man/calendar/add-event/',
  },
};

// Admin Endpoints (Security: /api/ad/)
export const ADMIN_ENDPOINTS = {
  APPOINTMENTS: {
    LIST: '/ad/appointments/',
    CREATE: '/ad/appointments/',
    UPDATE: (id: string | number) => `/ad/appointments/${id}/`,
    DELETE: (id: string | number) => `/ad/appointments/${id}/`,
  },
  STAFF: {
    LIST: '/ad/staff/',
    CREATE: '/ad/staff/',
    UPDATE: (id: string | number) => `/ad/staff/${id}/`,
    DELETE: (id: string | number) => `/ad/staff/${id}/`,
  },
  CUSTOMERS: {
    LIST: '/ad/customers/',
    DETAIL: (id: string | number) => `/ad/customers/${id}/`,
    UPDATE: (id: string | number) => `/ad/customers/${id}/`,
  },
  MANAGERS: {
    LIST: '/ad/managers/',
    CREATE: '/ad/managers/',
    UPDATE: (id: string | number) => `/ad/managers/${id}/`,
    DELETE: (id: string | number) => `/ad/managers/${id}/`,
    PERMISSIONS: (id: string | number) => `/ad/managers/${id}/permissions/`,
  },
  SERVICES: {
    LIST: '/ad/services/',
    CREATE: '/ad/services/',
    UPDATE: (id: string | number) => `/ad/services/${id}/`,
    DELETE: (id: string | number) => `/ad/services/${id}/`,
  },
  SUBSCRIPTIONS: {
    LIST: '/ad/subscriptions/',
    DETAIL: (id: string | number) => `/ad/subscriptions/${id}/`,
    UPDATE: (id: string | number) => `/ad/subscriptions/${id}/`,
    CANCEL: (id: string | number) => `/ad/subscriptions/${id}/cancel/`,
    APPOINTMENTS: (id: string | number) => `/ad/subscriptions/${id}/appointments/`,
  },
  ORDERS: {
    LIST: '/ad/orders/',
    DETAIL: (id: string | number) => `/ad/orders/${id}/`,
    UPDATE: (id: string | number) => `/ad/orders/${id}/`,
    APPROVE_CHANGE: (id: string | number) => `/ad/orders/${id}/approve-change/`,
    CANCEL: (id: string | number) => `/ad/orders/${id}/cancel/`,
    ITEMS: (id: string | number) => `/ad/orders/${id}/items/`,
  },
  REPORTS: {
    REVENUE: '/ad/reports/revenue/',
    APPOINTMENTS: '/ad/reports/appointments/',
    STAFF_PERFORMANCE: '/ad/reports/staff-performance/',
    SUBSCRIPTIONS: '/ad/reports/subscriptions/',
    ORDERS: '/ad/reports/orders/',
  },
  CALENDAR: {
    CONNECT: '/ad/calendar/connect/',
    STATUS: '/ad/calendar/status/',
    SYNC: '/ad/calendar/sync/',
    DISCONNECT: '/ad/calendar/disconnect/',
    EVENTS: '/ad/calendar/events/',
    ADD_EVENT: '/ad/calendar/add-event/',
    BULK_SYNC: '/ad/calendar/bulk-sync/',
  },
};
