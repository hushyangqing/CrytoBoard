import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

interface CryptoData {
    name: string;
    price: number;
    symbol: string;
}

interface HistoryData {
    [key: string]: [number, number][];
}

function Price() {
    // State to hold price data
    const [prices, setPrices] = useState<CryptoData[]>([]);
    const [history, setHistory] = useState<HistoryData>({});

    // Fetch price data from the backend on component mount
    useEffect(() => {
        axios.get('http://127.0.0.1:5000/top10_current_prices')
            .then(response => setPrices(response.data))
            .catch(error => console.error('Error fetching price data:', error));
    }, []);

    // Fetch last 24h price data for each cryptocurrency
    useEffect(() => {
        if (prices.length > 0) {
            const oneDayAgo = new Date();
            oneDayAgo.setDate(oneDayAgo.getDate() - 1);
            const timestamp = oneDayAgo.toISOString();
    
            prices.forEach(crypto => {
                axios.get(`http://127.0.0.1:5000/historyPrice/${crypto.symbol}?since=${timestamp}`)
                    .then(response => setHistory(prevHistory => ({
                        ...prevHistory,
                        [crypto.symbol]: response.data
                    })))
                    .catch(error => console.error(`Error fetching history data for ${crypto.symbol}:`, error));
    
                axios.get(`http://127.0.0.1:5000/currentPrice/${crypto.symbol}`)
                    .then(response => setHistory(prevHistory => ({
                        ...prevHistory,
                        [crypto.symbol]: [
                            ...prevHistory[crypto.symbol],
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
                display: true,
            },
            y: {
                display: false,
            },
        },
        plugins: {
            legend: {
                display: false,
            },
        },
    };

    return (
        <div>
            <h2>Top 10 Cryptocurrency Prices</h2>
            <table>
                <thead>
                    <tr>
                        <th>Number</th>
                        <th>Crypto Name</th>
                        <th>Crypto Price</th>
                        <th>Last 24h Graph</th>
                    </tr>
                </thead>
                <tbody>
                    {prices.map((crypto, index) => (
                        <tr key={crypto.symbol}>
                            <td>{index + 1}</td>
                            <td>{crypto.name}</td>
                            <td>${crypto.price.toFixed(2)}</td>
                            <td>
                                {history[crypto.symbol] ? (
                                    <Line data={getChartData(crypto.symbol)} options={chartOptions}/>
                                ) : (
                                    'Loading...'
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Price;
