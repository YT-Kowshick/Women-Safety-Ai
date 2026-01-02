import { Shield, TrendingUp, Map, AlertTriangle, Users, BarChart3 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MainLayout } from "@/components/layout/MainLayout";
import { SafetyScoreCard } from "@/components/common/SafetyScoreCard";
import { getNationalAverageScore } from "@/data/mockData";
import { Link } from "react-router-dom";

const features = [
  {
    title: "Data-Driven Safety Check",
    description: "Check historical safety scores for any state and year (2001-2021)",
    icon: Shield,
    path: "/safety-check",
  },
  {
    title: "What-If Simulation",
    description: "Simulate safety scores based on projected crime scenarios",
    icon: BarChart3,
    path: "/simulation",
  },
  {
    title: "Crime Trend Analysis",
    description: "Visualize crime patterns over 20 years with interactive charts",
    icon: TrendingUp,
    path: "/trends",
  },
  {
    title: "Risk Heatmap",
    description: "Geographic visualization of crime intensity across India",
    icon: Map,
    path: "/heatmap",
  },
  {
    title: "State Leaderboard",
    description: "See which states need the most attention for safety improvement",
    icon: Users,
    path: "/leaderboard",
  },
  {
    title: "SOS Emergency",
    description: "Prepare emergency alerts with one-click WhatsApp messaging",
    icon: AlertTriangle,
    path: "/sos",
    critical: true,
  },
];

export default function Dashboard() {
  const nationalScore = getNationalAverageScore();

  return (
    <MainLayout>
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl gradient-border p-8 md:p-12 mb-8">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-14 h-14 rounded-xl gradient-bg">
              <Shield className="w-7 h-7 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold gradient-text">AI-GUARD</h1>
              <p className="text-lg text-muted-foreground">Women Safety Intelligence</p>
            </div>
          </div>
          
          <p className="text-xl md:text-2xl text-foreground/90 font-light max-w-2xl mb-6">
            Data-driven risk insights • Heatmaps • SOS Emergency
          </p>
          
          <p className="text-muted-foreground max-w-3xl leading-relaxed">
            AI-GUARD empowers women, families, NGOs, and policymakers with actionable safety intelligence. 
            Using 20 years of historical data (2001-2021), our platform provides comprehensive risk analysis, 
            predictive insights, and emergency response preparation to reduce panic-time decision making.
          </p>
        </div>
      </div>

      {/* National Score */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <SafetyScoreCard
          score={nationalScore.score}
          riskLevel={nationalScore.riskLevel}
          title="National Average"
          subtitle="Based on 2021 data across all states"
          size="lg"
          className="lg:col-span-1"
        />
        
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>How AI-GUARD Works</CardTitle>
            <CardDescription>
              Three pillars of women safety intelligence
            </CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex flex-col items-center text-center p-4 rounded-xl bg-muted/50">
              <div className="w-12 h-12 rounded-full gradient-bg flex items-center justify-center mb-3">
                <BarChart3 className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="font-semibold mb-1">Analyze</h3>
              <p className="text-sm text-muted-foreground">
                Historical crime data processed into actionable safety scores
              </p>
            </div>
            <div className="flex flex-col items-center text-center p-4 rounded-xl bg-muted/50">
              <div className="w-12 h-12 rounded-full gradient-bg flex items-center justify-center mb-3">
                <TrendingUp className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="font-semibold mb-1">Predict</h3>
              <p className="text-sm text-muted-foreground">
                What-if simulations to understand risk under different scenarios
              </p>
            </div>
            <div className="flex flex-col items-center text-center p-4 rounded-xl bg-muted/50">
              <div className="w-12 h-12 rounded-full gradient-bg flex items-center justify-center mb-3">
                <AlertTriangle className="w-6 h-6 text-primary-foreground" />
              </div>
              <h3 className="font-semibold mb-1">Respond</h3>
              <p className="text-sm text-muted-foreground">
                One-click SOS preparation with WhatsApp deep-linking
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feature Grid */}
      <h2 className="text-xl font-semibold mb-4">Platform Features</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {features.map((feature) => (
          <Link key={feature.path} to={feature.path}>
            <Card className={`h-full transition-all duration-200 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 cursor-pointer group ${feature.critical ? 'border-destructive/30 hover:border-destructive' : ''}`}>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110 ${feature.critical ? 'bg-destructive/20' : 'gradient-bg'}`}>
                    <feature.icon className={`w-5 h-5 ${feature.critical ? 'text-destructive' : 'text-primary-foreground'}`} />
                  </div>
                  <CardTitle className={`text-base ${feature.critical ? 'text-destructive' : ''}`}>
                    {feature.title}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </MainLayout>
  );
}
