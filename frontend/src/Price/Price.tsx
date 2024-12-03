import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import {Context} from "../App";
import "./Price.css"

interface CryptoData {
    name: string;
    price: number;
    symbol: string;
}

interface HistoryData {
    [key: string]: [number, number][];
}

interface GrowthRateData {
    [key: string]: any;
}

const host = "http://127.0.0.1:5000/"

const getCryptoIcon = (cryptoName: string): string => {
    try {
        // Dynamically import the icon based on the crypto name
        return require(`../icons/${cryptoName}.png`);
    } catch (error) {
        // Fallback to default icon if not found
        return require('../icons/default.png');
    }
};

function Price() {
    // State to hold price data
    const [prices, setPrices] = useState<CryptoData[]>([]);
    const [history, setHistory] = useState<HistoryData>({});
    const [growthRate, setGrowthRate] = useState<GrowthRateData>({});
    const context = useContext(Context);

    if (!context) {
        throw new Error('useContext must be used within a Provider');
    }

    const { setShowPop } = context;

    // Fetch price data from the backend on component mount
    useEffect(() => {
        axios.get(`${host}top10_current_prices`)
            .then(response => setPrices(response.data))
            .catch(error => console.error('Error fetching price data:', error));
        axios.get(`${host}statistics/growth_rate`)
            .then(response => {
               let res: Record<string, string> = {};
               response.data.forEach((item: Record<string, string>) => {
                   for (let key in item) {
                       res[key] = item[key];
                   }
               })
               setGrowthRate(res);
            })
            .catch(error => console.error('Error fetching growth rate data:', error));
    }, []);

    // Fetch last 24h price data for each cryptocurrency
    useEffect(() => {
        if (prices.length > 0) {
            const oneDayAgo = new Date();
            oneDayAgo.setDate(oneDayAgo.getDate() - 1);
            const timestamp = oneDayAgo.toISOString();
            // console.log(timestamp);
            prices.forEach(crypto => {
                axios.get(`${host}historyPrice/${crypto.symbol}?since=${timestamp}`)
                    .then(response => setHistory(prevHistory => ({
                        ...prevHistory,
                        [crypto.symbol]: response.data
                    })))
                    .catch(error => console.error(`Error fetching history data for ${crypto.symbol}:`, error));
    
                axios.get(`${host}currentPrice/${crypto.symbol}`)
                    .then(response => setHistory(prevHistory => ({
                        ...prevHistory,
                        [crypto.symbol]: [
                            ...(prevHistory[crypto.symbol] || []),
                            [new Date().getTime(), response.data.price]
                        ]
                    })))
                    .catch(error => console.error(`Error fetching current price for ${crypto.symbol}:`, error));
            });
        }
    }, [prices]);

    // plot history price chart
    const getChartData = (cryptoSymbol: string) => {
        const data = history[cryptoSymbol];
        if (!data) {
            return {
                labels: [],
                datasets: [
                    {
                        label: 'Price',
                        data: [],
                        fill: false,
                        backgroundColor: 'rgba(75,192,192,0.4)',
                        borderColor: 'rgba(75,192,192,1)',
                    },
                ],
            };
        }

        return {
            labels: data.map(entry => new Date(entry[0] * 1000).toLocaleTimeString()),
            datasets: [
                {
                    label: 'Price',
                    data: data.map(entry => entry[1]),
                    fill: false,
                    backgroundColor: 'rgba(75,192,192,0.4)',
                    borderColor: 'rgba(75,192,192,1)',
                },
            ],
        };
    };

    const chartOptions = {
        scales: {
            x: {
                display: false,
            },
            y: {
                display: false,
            },
        },
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
        },
    };

    const showGrowthRate = (data: string) => {
        if (data === 'Infinite')
            return "🔥"
        if (data === 'None')
            return "-"
        return data
    }

    return (
        <div className="price">
            <h2 style={{textAlign: "center"}}>Top 10 Trending Cryptocurrencies</h2>
            <table style={{ width: "100%", borderCollapse: 'collapse', marginTop: '2vw' }}>
                <thead>
                    <tr>
                        <th style={{textAlign: 'center', padding: '10px 20px', width: "4vw", borderBottom: "1px solid black"}}># Rank</th>
                        <th style={{textAlign: 'center', padding: '10px 20px', width: "4vw", borderBottom: "1px solid black"}}>Crypto</th>
                        <th style={{textAlign: 'center', padding: '10px 20px', width: "10vw", borderBottom: "1px solid black"}}>Grow Rate of Popularity</th>
                        <th style={{textAlign: 'center', padding: '10px 20px', width: "4vw", borderBottom: "1px solid black"}}>Price</th>
                        <th style={{textAlign: 'center', padding: '10px 20px', width: "15vw", borderBottom: "1px solid black"}}>Price Trend</th>
                    </tr>
                </thead>
                <tbody>
                    {prices.map((crypto, index) => (
                        <tr key={crypto.symbol}
                            onClick={() => {
                                setShowPop(crypto.symbol);
                                console.log("clicked: ", crypto.symbol);
                            }
                        }>
                            <td style={{textAlign: "center"}}>{index + 1}</td>
                            <td>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <img
                                        src={getCryptoIcon(crypto.name)}
                                        alt={`${crypto.name} icon`}
                                        width="24px"
                                        height="24px"
                                        onError={(e) => (e.currentTarget.src = require('../icons/default.png'))}
                                    />
                                    <span>{crypto.name}</span>
                                </div>
                            </td>
                            <td style={{textAlign: "center"}}>{showGrowthRate(growthRate[crypto.symbol])}</td>
                            <td style={{textAlign: "center"}}>${crypto.price.toFixed(2)}</td>
                            <td style={{ display: "flex", justifyContent: 'center'}}>
                                <div style={{ width:'25vw', height: '15vh', display: "block"}}>
                                    {history[crypto.symbol] ? (
                                        <Line data={getChartData(crypto.symbol)} options={chartOptions}/>
                                    ) : (
                                        'Loading...'
                                    )}
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Price;
export {host};
