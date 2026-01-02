import { useState } from "react";
import { Shield } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { SafetyScoreCard } from "@/components/common/SafetyScoreCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { INDIAN_STATES, YEARS, calculateSafetyScore, type IndianState } from "@/data/mockData";

export default function SafetyCheck() {
  const [selectedState, setSelectedState] = useState<IndianState | null>(null);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);

  const result = selectedState && selectedYear 
    ? calculateSafetyScore(selectedState, selectedYear) 
    : null;

  return (
    <MainLayout>
      <PageHeader
        title="Safety Check"
        subtitle="View historical safety scores based on 20 years of crime data"
        icon={<Shield className="w-6 h-6 text-primary-foreground" />}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Selection Panel */}
        <Card>
          <CardHeader>
            <CardTitle>Select Location & Year</CardTitle>
            <CardDescription>
              Choose a state and year to view the historical safety assessment
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">State</label>
              <Select onValueChange={(value) => setSelectedState(value as IndianState)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a state" />
                </SelectTrigger>
                <SelectContent>
                  {INDIAN_STATES.map((state) => (
                    <SelectItem key={state} value={state}>
                      {state}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Year</label>
              <Select onValueChange={(value) => setSelectedYear(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a year" />
                </SelectTrigger>
                <SelectContent>
                  {YEARS.map((year) => (
                    <SelectItem key={year} value={year.toString()}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedState && selectedYear && (
              <div className="pt-4 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  Showing safety assessment for <span className="font-medium text-foreground">{selectedState}</span> in <span className="font-medium text-foreground">{selectedYear}</span>
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Panel */}
        <div className="flex items-center justify-center">
          {result ? (
            <SafetyScoreCard
              score={result.score}
              riskLevel={result.riskLevel}
              title={`${selectedState} Safety Score`}
              subtitle={`Historical data from ${selectedYear}`}
              size="lg"
            />
          ) : (
            <Card className="w-full max-w-sm text-center">
              <CardContent className="pt-12 pb-12">
                <div className="w-20 h-20 mx-auto rounded-full bg-muted flex items-center justify-center mb-4">
                  <Shield className="w-10 h-10 text-muted-foreground" />
                </div>
                <p className="text-muted-foreground">
                  Select a state and year to view the safety score
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Info Section */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="text-lg">About Safety Scores</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-safety-high/20 flex items-center justify-center shrink-0">
              <span className="text-safety-high font-bold text-sm">70+</span>
            </div>
            <div>
              <h4 className="font-medium text-safety-high">Low Risk</h4>
              <p className="text-sm text-muted-foreground">
                Standard precautions are sufficient. Generally safe environment.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-safety-medium/20 flex items-center justify-center shrink-0">
              <span className="text-safety-medium font-bold text-sm">40-69</span>
            </div>
            <div>
              <h4 className="font-medium text-safety-medium">Medium Risk</h4>
              <p className="text-sm text-muted-foreground">
                Enhanced awareness recommended. Follow safety protocols.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-safety-low/20 flex items-center justify-center shrink-0">
              <span className="text-safety-low font-bold text-sm">&lt;40</span>
            </div>
            <div>
              <h4 className="font-medium text-safety-low">High Risk</h4>
              <p className="text-sm text-muted-foreground">
                Exercise caution. Keep emergency contacts readily available.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </MainLayout>
  );
}
