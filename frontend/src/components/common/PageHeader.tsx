import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, subtitle, icon, children, className }: PageHeaderProps) {
  return (
    <div className={cn("flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8", className)}>
      <div className="flex items-center gap-4">
        {icon && (
          <div className="flex items-center justify-center w-12 h-12 rounded-xl gradient-bg">
            {icon}
          </div>
        )}
        <div>
          <h1 className="text-2xl md:text-3xl font-bold gradient-text">{title}</h1>
          {subtitle && (
            <p className="text-sm md:text-base text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
      </div>
      {children && <div className="flex items-center gap-3">{children}</div>}
    </div>
  );
}
