import { useEffect, useRef } from "react";
import { useLocation } from "react-router";
import { isInAppNavigation } from "./navigation";

type PageTitleProps = {
  /** Sidens H1. Dokumenttittelen blir «{title} – Red Ball Express». */
  title: string;
  className?: string;
};

/**
 * Sidens H1 (UX-DR21): setter dokumenttittelen og tar fokus ved hvert sidebytte i appen,
 * men ikke ved første lasting av dokumentet.
 */
export function PageTitle({ title, className }: PageTitleProps) {
  const ref = useRef<HTMLHeadingElement>(null);
  const { key } = useLocation();

  useEffect(() => {
    document.title = `${title} – Red Ball Express`;
  }, [title]);

  useEffect(() => {
    if (isInAppNavigation(key)) {
      ref.current?.focus();
    }
  }, [key]);

  return (
    <h1 ref={ref} className={className} tabIndex={-1}>
      {title}
    </h1>
  );
}
