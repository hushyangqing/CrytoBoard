import React, { useEffect, useState, useRef } from 'react';
import Highcharts from 'highcharts';
import axios from 'axios';
import './Chart.css';

function Chart() {
    const chartContainer = useRef<HTMLDivElement>(null);
    const [activeTab, setActiveTab] = useState<'articles' | 'frequency'>('articles');
    const chartInstance = useRef<Highcharts.Chart | null>(null);
    const [chartData, setChartData] = useState<any[]>([]);

    // MOCK DATA
    const mockData = [
        {
            "BBC": {
                "numberOfArticle": [
                    {"BTC": 12}, {"ETH": 8}, {"USDT": 3}, {"BNB": 4}, 
                    {"SOL": 7}, {"USDC": 2}, {"XRP": 5}, {"DOGE": 6}, 
                    {"TRX": 2}, {"TON": 1}
                ],
                "wordFrequency": {
                    "BTC": 45, "ETH": 28, "USDT": 8, "BNB": 12,
                    "SOL": 25, "USDC": 4, "XRP": 15, "DOGE": 22,
                    "TRX": 5, "TON": 2
                }
            }
        },
        {
            "NYTimes": {
                "numberOfArticle": [
                    {"BTC": 15}, {"ETH": 10}, {"USDT": 2}, {"BNB": 3},
                    {"SOL": 8}, {"USDC": 1}, {"XRP": 4}, {"DOGE": 7},
                    {"TRX": 1}, {"TON": 2}
                ],
                "wordFrequency": {
                    "BTC": 52, "ETH": 35, "USDT": 5, "BNB": 9,
                    "SOL": 30, "USDC": 2, "XRP": 12, "DOGE": 28,
                    "TRX": 3, "TON": 4
                }
            }
        },
        {
            "X": {
                "numberOfArticle": [
                    {"BTC": 150}, {"ETH": 120}, {"USDT": 45}, {"BNB": 60},
                    {"SOL": 95}, {"USDC": 30}, {"XRP": 70}, {"DOGE": 85},
                    {"TRX": 25}, {"TON": 20}
                ],
                "wordFrequency": {
                    "BTC": 480, "ETH": 350, "USDT": 120, "BNB": 180,
                    "SOL": 285, "USDC": 75, "XRP": 210, "DOGE": 255,
                    "TRX": 65, "TON": 45
                }
            }
        }
    ];

    // Fetch data from backend
    useEffect(() => {
        axios.get('http://127.0.0.1:5000/chart_data')
            .then(response => {
                setChartData(response.data);
                updateChart();
            })
            .catch(error => {
                console.error('Error fetching chart data:', error);
            });
    }, []);

    const transformData = (rawData: any[], type: 'articles' | 'frequency'): Highcharts.Options => {
        const sources = ['BBC', 'NYTimes', 'X'];
        const cryptos = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'DOGE', 'TRX', 'TON'];
        
        const series = sources.map(source => {
            const sourceData = rawData.find(item => item[source]);
            return {
                name: source,
                data: cryptos.map(crypto => {
                    if (type === 'articles') {
                        const articleData = sourceData[source].numberOfArticle.find((item: any) => 
                            Object.keys(item)[0] === crypto
                        );
                        return articleData ? Object.values(articleData)[0] : 0;
                    } else {
                        return sourceData[source].wordFrequency[crypto] || 0;
                    }
                })
            };
        });

        return {
            chart: {
                type: 'column'
            },
            title: {
                text: type === 'articles' ? 'Number of Articles by Media Source' : 'Word Frequency by Media Source',
                align: 'left'
            },
            xAxis: {
                categories: cryptos,
                title: {
                    text: 'Cryptocurrencies'
                }
            },
            yAxis: {
                min: 0,
                title: {
                    text: type === 'articles' ? 'Number of Articles' : 'Word Frequency'
                },
                stackLabels: {
                    enabled: true
                }
            },
            legend: {
                align: 'right',
                verticalAlign: 'top',
                backgroundColor: 'white',
                borderColor: '#CCC',
                borderWidth: 1,
                shadow: false,
                padding: 8,
                margin: 0,
                itemMarginTop: 2,
                itemMarginBottom: 2
            },
            tooltip: {
                headerFormat: '<b>{point.x}</b><br/>',
                pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
            },
            plotOptions: {
                column: {
                    stacking: 'normal',
                    dataLabels: {
                        enabled: false
                    }
                }
            },
            credits: {
                enabled: false
            },
            series: series as Highcharts.SeriesOptionsType[]
        };
    };

    const createChart = () => {
        if (chartContainer.current && !chartInstance.current && chartData.length > 0) {
            // const options = transformData(chartData, activeTab);
            const options = transformData(mockData, activeTab);
            chartInstance.current = Highcharts.chart(chartContainer.current, options);
        }
    };

    const updateChart = () => {
        if (chartInstance.current && chartData.length > 0) {
            // const options = transformData(chartData, activeTab);
            const options = transformData(mockData, activeTab);
            chartInstance.current.update(options, true, true);
        } else if (chartData.length > 0) {
            createChart();
        }
    };

    useEffect(() => {
        createChart();
        return () => {
            if (chartInstance.current) {
                try {
                    chartInstance.current.destroy();
                    chartInstance.current = null;
                } catch (e) {
                    console.error('Error destroying chart:', e);
                }
            }
        };
    }, [mockData]);
    // }, [chartData]); 

    useEffect(() => {
        updateChart();
    }, [activeTab, mockData]);
    // }, [activeTab, chartData]);

    const handleTabClick = (tab: 'articles' | 'frequency') => {
        setActiveTab(tab);
    };

    return (
        <div className="chart-container">
            <div className="chart-tabs">
                <button 
                    className={`chart-tab ${activeTab === 'articles' ? 'active' : ''}`}
                    onClick={() => handleTabClick('articles')}
                >
                    Number of Articles
                </button>
                <button 
                    className={`chart-tab ${activeTab === 'frequency' ? 'active' : ''}`}
                    onClick={() => handleTabClick('frequency')}
                >
                    Word Frequency
                </button>
            </div>
            <div ref={chartContainer} className="chart-content">
                {chartData.length === 0 && <div className="loading">Loading chart data...</div>}
            </div>
        </div>
    );
}

export default Chart;