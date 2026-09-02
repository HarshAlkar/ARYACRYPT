/** Shared brand strings — do not hardcode elsewhere. */

export const PRODUCT_NAME = "ARYACRYPT";
export const PRODUCT_NAME_DISPLAY = "AryaCrypt";
export const PRODUCT_TAGLINE = "Cryptographic Security Framework";
export const FRAMEWORK_VERSION = "1.1.0";
export const COPYRIGHT_YEAR = 2026;

export const BRAND = {
  product: PRODUCT_NAME,
  productDisplay: PRODUCT_NAME_DISPLAY,
  tagline: PRODUCT_TAGLINE,
  version: FRAMEWORK_VERSION,
  versionLabel: `${PRODUCT_NAME} v${FRAMEWORK_VERSION}`,
  copyright: `© ${COPYRIGHT_YEAR} ${PRODUCT_NAME_DISPLAY}. All rights reserved.`,
  footerBlurb: PRODUCT_TAGLINE,
} as const;
