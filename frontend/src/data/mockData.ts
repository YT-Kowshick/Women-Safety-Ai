// Mock data for AI-GUARD Women Safety Intelligence Platform
// Based on historical crimes-against-women data (India, 2001–2021)

export const INDIAN_STATES = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Delhi",
] as const;

export const YEARS = Array.from({ length: 21 }, (_, i) => 2001 + i);

export const CRIME_TYPES = [
  "Rape",
  "Assault on Women",
  "Kidnapping & Abduction",
  "Domestic Violence",
  "Women Trafficking",
] as const;

export type CrimeType = (typeof CRIME_TYPES)[number];
export type IndianState = (typeof INDIAN_STATES)[number];

// Safety score calculation (mock - in reality this would be ML-based)
export function calculateSafetyScore(
  state: IndianState,
  year: number
): { score: number; riskLevel: "Low" | "Medium" | "High" } {
  // Seed based on state and year for consistent results
  const seed = state.length * year;
  const baseScore = 40 + (seed % 50);
  const yearFactor = (year - 2001) * 0.5;
  const score = Math.min(100, Math.max(0, Math.round(baseScore + yearFactor)));
  
  const riskLevel = score >= 70 ? "Low" : score >= 40 ? "Medium" : "High";
  
  return { score, riskLevel };
}

// Simulate safety score based on crime sliders
export function simulateSafetyScore(crimeValues: Record<CrimeType, number>): {
  score: number;
  riskLevel: "Low" | "Medium" | "High";
  interpretation: string;
} {
  const weights: Record<CrimeType, number> = {
    "Rape": 0.25,
    "Assault on Women": 0.2,
    "Kidnapping & Abduction": 0.2,
    "Domestic Violence": 0.2,
    "Women Trafficking": 0.15,
  };

  const weightedSum = Object.entries(crimeValues).reduce(
    (acc, [crime, value]) => acc + value * weights[crime as CrimeType],
    0
  );

  const score = Math.round(100 - weightedSum);
  const riskLevel = score >= 70 ? "Low" : score >= 40 ? "Medium" : "High";
  
  const interpretations = {
    Low: "The projected safety level is favorable. Standard precautions are sufficient.",
    Medium: "Moderate risk detected. Enhanced awareness and safety protocols recommended.",
    High: "Elevated risk scenario. Immediate safety measures and emergency contacts should be readily available.",
  };

  return { score, riskLevel, interpretation: interpretations[riskLevel] };
}

// Generate mock crime trend data
export function getCrimeTrendData(
  state: IndianState,
  crimeType: CrimeType
): { year: number; count: number; movingAvg?: number }[] {
  const seed = state.length + crimeType.length;
  const baseCount = 500 + (seed % 2000);
  
  const data = YEARS.map((year, index) => {
    const trend = Math.sin(index * 0.3) * 200;
    const noise = Math.sin(seed * year) * 100;
    const growth = index * 15;
    const count = Math.max(0, Math.round(baseCount + trend + noise + growth));
    
    return { year, count };
  });

  // Calculate 3-year moving average
  return data.map((item, index) => {
    if (index >= 2) {
      const avg = Math.round(
        (data[index].count + data[index - 1].count + data[index - 2].count) / 3
      );
      return { ...item, movingAvg: avg };
    }
    return item;
  });
}

// Get heatmap data for all states
export function getHeatmapData(crimeType: CrimeType): {
  state: IndianState;
  intensity: number;
  count: number;
}[] {
  return INDIAN_STATES.map((state) => {
    const seed = state.length * crimeType.length;
    const intensity = (seed % 100) / 100;
    const count = Math.round(intensity * 5000 + 500);
    return { state, intensity, count };
  });
}

// Leaderboard data (states with lowest safety scores)
export function getLeaderboardData(): {
  rank: number;
  state: IndianState;
  score: number;
  riskLevel: "Low" | "Medium" | "High";
}[] {
  const latestYear = 2021;
  
  const statesWithScores = INDIAN_STATES.map((state) => ({
    state,
    ...calculateSafetyScore(state, latestYear),
  }));

  return statesWithScores
    .sort((a, b) => a.score - b.score)
    .slice(0, 10)
    .map((item, index) => ({
      rank: index + 1,
      state: item.state,
      score: item.score,
      riskLevel: item.riskLevel,
    }));
}

// Safety recommendations based on score
export function getSafetyRecommendations(score: number): {
  riskLevel: "Low" | "Medium" | "High";
  tips: string[];
} {
  if (score >= 70) {
    return {
      riskLevel: "Low",
      tips: [
        "Maintain regular communication with family about your whereabouts",
        "Keep emergency contacts saved on speed dial",
        "Stay aware of your surroundings, especially in unfamiliar areas",
        "Share your live location with trusted contacts during travel",
        "Trust your instincts — if something feels wrong, leave the situation",
      ],
    };
  } else if (score >= 40) {
    return {
      riskLevel: "Medium",
      tips: [
        "Avoid isolated areas, especially after dark",
        "Travel in groups when possible",
        "Keep your phone fully charged when going out",
        "Inform family/friends about your travel plans in advance",
        "Familiarize yourself with nearby police stations and safe zones",
        "Consider carrying personal safety devices (whistle, pepper spray where legal)",
        "Use verified transportation services and share trip details",
      ],
    };
  } else {
    return {
      riskLevel: "High",
      tips: [
        "Limit travel to essential journeys only",
        "Always travel with trusted companions",
        "Keep emergency services numbers readily accessible",
        "Share real-time location with multiple trusted contacts",
        "Avoid public confrontations — prioritize de-escalation",
        "Know the locations of hospitals, police stations, and women's shelters",
        "Consider using SOS apps that alert multiple contacts simultaneously",
        "Have a safety plan discussed with family for emergency situations",
        "Stay connected — check in regularly with family/friends",
      ],
    };
  }
}

// National average safety score
export function getNationalAverageScore(): {
  score: number;
  riskLevel: "Low" | "Medium" | "High";
} {
  const scores = INDIAN_STATES.map((state) => calculateSafetyScore(state, 2021).score);
  const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
  const riskLevel = avgScore >= 70 ? "Low" : avgScore >= 40 ? "Medium" : "High";
  
  return { score: avgScore, riskLevel };
}
