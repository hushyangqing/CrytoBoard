import './News.css'
import axios from "axios";
import {useEffect, useState} from "react";

interface NewsProps {
    crypto: string
}

interface NewsState {
    headline: string;
    source: string;
    timestamp: number;
    url: string;
    image_url: string;
}

const nameMapping: { [key: string]: string } = {'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'USDT': 'Tether',
    'BNB': 'BNB',
    'SOL': 'Solana',
    'USDC': 'USDC',
    'XRP': 'XRP',
    'DOGE': 'Dogecoin',
    'TRX': 'TRON',
    'TON': 'Toncoin',
    'ADA': 'Cardano',
    'SHIB': 'Shiba Inu',
    'AVAX': 'Avalanche',
    'BCH': 'Bitcoin Cash',
    'LINK': 'Chainlink',
    'DOT': 'Polkadot',
    'LEO': 'UNUS SED LEO',
    'SUI': 'Sui',
    'DAI': 'Dai',
    'LTC': 'Litecoin'}

function News({crypto}: NewsProps): JSX.Element {

    const [news, setNews] = useState<NewsState[]>([])

    useEffect(() => {
        axios.get(`http://127.0.0.1:5000/news/search?crypto_name=${crypto}`)
            .then(response => setNews(response.data))
            .catch(error => console.error(`Error fetching news for ${crypto}:`, error));
    }, [crypto]);

    const singlePiece = (data: NewsState) => {
        const date = new Date(data.timestamp * 1000);
        // console.log(data.timestamp);
        const formattedDate = date.toLocaleDateString('en-US', {
            month: 'short',  // 缩写月份
            day: 'numeric',  // 日期
            year: 'numeric', // 年份
        });

        return <div className="wholePiece">
            <img className="newsImage" src={data.image_url} alt="img"/>
            <div className="singlePiece">
                <div className="singlePieceTitle">
                    <div style={{fontSize: "1vw", fontWeight: "bold"}}>{formattedDate}</div>
                    <div style={{ fontSize: "calc(1vw - 5px)"}}>from {data.source}</div>
                </div>
                <div className="singlePieceContent">{data.headline}</div>
                <div className="dividerSub"/>
            </div>
        </div>
    }

    return (<div className="background">
        <div className="newsBox">
            <div className="newsTitle">
                <div className="newsTitleName">Top News of {nameMapping[crypto]}</div>
                <div className="newsTitleCrypto">{crypto}</div>
                <div className="close">X</div>
            </div>
            <div className="titleBackground"/>
            <div className="divider"/>
            {news.map((data) => singlePiece(data))}
        </div>
    </div>)
}

export default News;