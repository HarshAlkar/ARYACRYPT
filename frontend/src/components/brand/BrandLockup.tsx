import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import {
  BRAND,
  PRODUCT_NAME,
  PRODUCT_NAME_DISPLAY,
  PRODUCT_TAGLINE,
} from "@/brand/constants";

type Variant = "nav" | "hero" | "sidebar" | "compact";

interface BrandLockupProps {
  variant?: Variant;
  to?: string | null;
  className?: string;
}

export function BrandLockup({
  variant = "nav",
  to = "/",
  className = "",
}: BrandLockupProps) {
  const wrap = (node: ReactNode) =>
    to ? (
      <Link to={to} className={`group inline-flex flex-col ${className}`}>
        {node}
      </Link>
    ) : (
      <div className={`inline-flex flex-col ${className}`}>{node}</div>
    );

  if (variant === "hero") {
    return wrap(
      <>
        <span className="font-sans text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-slate-50">
          {PRODUCT_NAME}
        </span>
        <span className="mt-4 text-base sm:text-lg text-slate-400 font-normal tracking-wide">
          {PRODUCT_TAGLINE}
        </span>
      </>
    );
  }

  if (variant === "sidebar") {
    return wrap(
      <span className="text-lg font-bold tracking-tight text-slate-100 group-hover:text-sky-300 transition-colors">
        {PRODUCT_NAME}
      </span>
    );
  }

  if (variant === "compact") {
    return wrap(
      <span className="font-sans text-sm font-semibold tracking-tight text-slate-200">
        {PRODUCT_NAME_DISPLAY}
        <span className="ml-2 text-xs font-normal text-slate-500">
          v{BRAND.version}
        </span>
      </span>
    );
  }

  return wrap(
    <span className="text-lg font-bold tracking-tight text-slate-100 group-hover:text-sky-300 transition-colors">
      {PRODUCT_NAME}
    </span>
  );
}
