/** Shared brand strings — do not hardcode elsewhere. */

export const COMPANY_NAME = "TIVRA";
export const PRODUCT_NAME = "ARYACRYPT";
export const PRODUCT_NAME_DISPLAY = "AryaCrypt";
export const PRODUCT_TAGLINE = "Cryptographic Security Framework";
export const COMPANY_ATTRIBUTION = "A TIVRA Technology";
export const CREATOR_ATTRIBUTION = "Created by Harsh Alkar";
export const FRAMEWORK_VERSION = "1.1.0";
export const COPYRIGHT_YEAR = 2026;

export const BRAND = {
  company: COMPANY_NAME,
  product: PRODUCT_NAME,
  productDisplay: PRODUCT_NAME_DISPLAY,
  tagline: PRODUCT_TAGLINE,
  companyLine: COMPANY_ATTRIBUTION,
  creator: CREATOR_ATTRIBUTION,
  version: FRAMEWORK_VERSION,
  versionLabel: `${PRODUCT_NAME} v${FRAMEWORK_VERSION}`,
  copyright: `© ${COPYRIGHT_YEAR} ${COMPANY_NAME}. All rights reserved.`,
  footerBlurb: `A cryptographic security framework by ${COMPANY_NAME}.`,
} as const;
