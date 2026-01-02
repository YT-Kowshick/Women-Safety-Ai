import { useState } from "react";
import { FlaskConical, RotateCcw } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { SafetyScoreCard } from "@/components/common/SafetyScoreCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { CRIME_TYPES, simulateSafetyScore, type CrimeType } from "@/data/mockData";

const DEFAULT_VALUES: Record<CrimeType, number> = {
  "Rape": 50,
  "Assault on Women": 50,
  "Kidnapping & Abduction": 50,
  "Domestic Violence": 50,
  "Women Trafficking": 50,
};

export default function Simulation() {
  const [crimeValues, setCrimeValues] = useState<Record<CrimeType, number>>(DEFAULT_VALUES);
  const [result, setResult] = useState<ReturnType<typeof simulateSafetyScore> | null>(null);

  const handleSliderChange = (crime: CrimeType, value: number[]) => {
    setCrimeValues((prev) => ({ ...prev, [crime]: value[0] }));
  };

  const handleSimulate = () => {
    const simResult = simulateSafetyScore(crimeValues);
    setResult(simResult);
  };

  const handleReset = () => {
    setCrimeValues(DEFAULT_VALUES);
    setResult(null);
  };

  return (
    <MainLayout>
      <PageHeader
        title="What-If Crime Simulation"
        subtitle="Project safety scores based on hypothetical crime scenarios"
        icon={<FlaskConical className="w-6 h-6 text-primary-foreground" />}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sliders Panel */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Crime Rate Projections</CardTitle>
            <CardDescription>
              Adjust the sliders to simulate different crime intensity levels (0 = Low, 100 = Severe)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            {CRIME_TYPES.map((crime) => (
              <div key={crime} className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground">{crime}</label>
                  <span className="text-sm text-muted-foreground font-mono w-12 text-right">
                    {crimeValues[crime]}%
                  </span>
                </div>
                <Slider
                  value={[crimeValues[crime]]}
                  onValueChange={(value) => handleSliderChange(crime, value)}
                  max={100}
                  step={1}
                  className="cursor-pointer"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Low</span>
                  <span>Moderate</span>
                  <span>Severe</span>
                </div>
              </div>
            ))}

            <div className="flex gap-3 pt-4 border-t border-border">
              <Button onClick={handleSimulate} className="flex-1 gradient-bg">
                <FlaskConical className="w-4 h-4 mr-2" />
                Simulate Safety Score
              </Button>
              <Button variant="outline" onClick={handleReset}>
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Result Panel */}
        <div className="space-y-6">
          {result ? (
            <>
              <SafetyScoreCard
                score={result.score}
                riskLevel={result.riskLevel}
                title="Projected Score"
                subtitle="Based on simulation parameters"
                size="lg"
              />
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Risk Interpretation</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {result.interpretation}
                  </p>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="text-center">
              <CardContent className="pt-12 pb-12">
                <div className="w-20 h-20 mx-auto rounded-full bg-muted flex items-center justify-center mb-4">
                  <FlaskConical className="w-10 h-10 text-muted-foreground" />
                </div>
                <p className="text-muted-foreground">
                  Adjust the crime parameters and click "Simulate" to see the projected safety score
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Methodology Note */}
      <Card className="mt-8 border-primary/20">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            <strong className="text-foreground">Methodology Note:</strong> This simulation uses weighted 
            factors for different crime categories to project an overall safety score. The weights reflect 
            the relative severity and impact of each crime type on women's safety. This tool is designed 
            for scenario planning and awareness, not as a definitive predictor.
          </p>
        </CardContent>
      </Card>
    </MainLayout>
  );
}
