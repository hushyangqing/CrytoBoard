import React, { useEffect, useState, useRef } from 'react';
import Highcharts from 'highcharts';
import axios from 'axios';
import './Chart.css';

function Chart() {
    const chartContainer = useRef<HTMLDivElement>(null);
    const [activeTab, setActiveTab] = useState<'articles' | 'frequency'>('articles');
    const chartInstance = useRef<Highcharts.Chart | null>(null);
    const [chartData, setChartData] = useState<any[]>([]);

    const formatDateTime = (date: Date): string => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    };

    useEffect(() => {
        const endTime = new Date();
        const startTime = new Date(endTime.getTime() - (24 * 60 * 60 * 1000)); // 24 hours ago
        
        // USES MOCK START TIME
        const mockStartTimeStr = "2023-11-01T00:00:00"
        const startTimeStr = formatDateTime(startTime);
        const endTimeStr = formatDateTime(endTime);
    
        axios.get(`http://127.0.0.1:5000/chart_data`, {
            params: {
                // Replace with startTimeStr to get last 24 hours data
                start_time: mockStartTimeStr,
                end_time: endTimeStr
            }
        })
        .then(response => {
            setChartData(response.data);
            updateChart();
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
        });
    }, []);

    const transformData = (rawData: any[], type: 'articles' | 'frequency'): Highcharts.Options => {
        const sources = ['Fox', 'NYTimes', 'X'];
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
            const options = transformData(chartData, activeTab);
            chartInstance.current = Highcharts.chart(chartContainer.current, options);
        }
    };

    const updateChart = () => {
        if (chartInstance.current && chartData.length > 0) {
            const options = transformData(chartData, activeTab);
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
    }, [chartData]); 

    useEffect(() => {
        updateChart();
    }, [activeTab, chartData]);

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