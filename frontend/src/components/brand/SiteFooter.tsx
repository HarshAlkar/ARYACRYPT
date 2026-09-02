import { BRAND } from "@/brand/constants";

interface SiteFooterProps {
  className?: string;
}

export function SiteFooter({ className = "" }: SiteFooterProps) {
  return (
    <footer
      className={`border-t border-border/50 py-8 ${className}`}
      role="contentinfo"
    >
      <div className="container mx-auto px-4 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div className="space-y-1">
          <p className="text-sm font-semibold tracking-tight text-slate-200">
            {BRAND.product}
          </p>
          <p className="text-sm text-slate-500">{BRAND.footerBlurb}</p>
        </div>
        <p className="text-xs text-slate-600 md:text-right">{BRAND.copyright}</p>
      </div>
    </footer>
  );
}
