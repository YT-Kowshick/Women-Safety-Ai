import { useState } from "react";
import { Lightbulb, CheckCircle2 } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { getSafetyRecommendations } from "@/data/mockData";
import { cn } from "@/lib/utils";

export default function Recommendations() {
  const [score, setScore] = useState(50);
  const { riskLevel, tips } = getSafetyRecommendations(score);
  const colors = { Low: "text-safety-high border-safety-high", Medium: "text-safety-medium border-safety-medium", High: "text-safety-low border-safety-low" };

  return (
    <MainLayout>
      <PageHeader title="Safety Recommendations" subtitle="Context-aware tips based on risk level" icon={<Lightbulb className="w-6 h-6 text-primary-foreground" />} />
      <Card className="mb-8">
        <CardContent className="pt-6 space-y-4">
          <div className="flex justify-between"><span className="font-medium">Simulated Safety Score</span><span className={cn("font-bold", colors[riskLevel])}>{score} - {riskLevel} Risk</span></div>
          <Slider value={[score]} onValueChange={(v) => setScore(v[0])} max={100} />
          <div className="flex justify-between text-xs text-muted-foreground"><span>High Risk (0)</span><span>Low Risk (100)</span></div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle className={cn(colors[riskLevel])}>Recommendations for {riskLevel} Risk</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {tips.map((tip, i) => (
            <div key={i} className="flex gap-3 items-start"><CheckCircle2 className="w-5 h-5 text-primary shrink-0 mt-0.5" /><p className="text-sm text-muted-foreground">{tip}</p></div>
          ))}
        </CardContent>
      </Card>
    </MainLayout>
  );
}
