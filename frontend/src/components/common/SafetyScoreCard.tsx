import { cn } from "@/lib/utils";

interface SafetyScoreCardProps {
  score: number;
  riskLevel: "Low" | "Medium" | "High";
  title?: string;
  subtitle?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function SafetyScoreCard({
  score,
  riskLevel,
  title = "Safety Score",
  subtitle,
  size = "md",
  className,
}: SafetyScoreCardProps) {
  const colors = {
    Low: "text-safety-high border-safety-high",
    Medium: "text-safety-medium border-safety-medium",
    High: "text-safety-low border-safety-low",
  };

  const bgColors = {
    Low: "bg-safety-high/10",
    Medium: "bg-safety-medium/10",
    High: "bg-safety-low/10",
  };

  const glows = {
    Low: "shadow-[0_0_30px_hsl(142_76%_45%/0.2)]",
    Medium: "shadow-[0_0_30px_hsl(45_93%_47%/0.2)]",
    High: "shadow-[0_0_30px_hsl(0_84%_60%/0.2)]",
  };

  const sizes = {
    sm: "w-20 h-20 text-2xl",
    md: "w-28 h-28 text-4xl",
    lg: "w-36 h-36 text-5xl",
  };

  return (
    <div
      className={cn(
        "flex flex-col items-center gap-3 p-6 rounded-xl bg-card border border-border",
        glows[riskLevel],
        className
      )}
    >
      {title && <span className="text-sm text-muted-foreground font-medium">{title}</span>}
      
      <div
        className={cn(
          "flex items-center justify-center rounded-full border-4 font-bold",
          sizes[size],
          colors[riskLevel],
          bgColors[riskLevel]
        )}
      >
        {score}
      </div>
      
      <div className="flex flex-col items-center gap-1">
        <span
          className={cn(
            "text-sm font-semibold px-3 py-1 rounded-full",
            bgColors[riskLevel],
            colors[riskLevel]
          )}
        >
          {riskLevel} Risk
        </span>
        {subtitle && (
          <span className="text-xs text-muted-foreground text-center">{subtitle}</span>
        )}
      </div>
    </div>
  );
}
