'use client';

import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { PolarArea } from 'react-chartjs-2';

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend);

interface ScoreChartProps {
    semanticScore: number;
    keywordScore: number;
    completenessScore: number;
}

export default function ScoreChart({ semanticScore, keywordScore, completenessScore }: ScoreChartProps) {
    const data = {
        labels: ['Semantic Match', 'Keyword Coverage', 'Completeness'],
        datasets: [
            {
                label: 'Score (out of 100)',
                data: [semanticScore, keywordScore, completenessScore],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.5)', // Blue
                    'rgba(16, 185, 129, 0.5)', // Green
                    'rgba(139, 92, 246, 0.5)', // Purple
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(139, 92, 246, 1)',
                ],
                borderWidth: 1,
            },
        ],
    };

    const options = {
        responsive: true,
        scales: {
            r: {
                min: 0,
                max: 100,
                ticks: {
                    display: false,
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)',
                },
                angleLines: {
                    color: 'rgba(255, 255, 255, 0.1)',
                }
            },
        },
        plugins: {
            legend: {
                position: 'bottom' as const,
                labels: {
                    color: 'rgba(255, 255, 255, 0.8)',
                }
            },
        },
    };

    return (
        <div className="w-full h-64 flex justify-center items-center">
            <PolarArea data={data} options={options} />
        </div>
    );
}
