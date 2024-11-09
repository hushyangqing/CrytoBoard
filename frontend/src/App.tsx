import React from 'react';
import './App.css';
import Price from "./Price/Price";
import Chart from "./MediaTrends/Chart";
import BestNews from "./MediaTrends/BestNews";
import {useState} from "react";

function App() {
  const [tab, setTab] = useState<string>('price');

  const clickTab = (tabName: string) => {
    if (tab !== tabName) {
      setTab(tabName);
    }
  }

  return (
    <div>
      <div className="App-header">
        <div className="App-title">Crypto Board</div>
        <div
            className={tab === 'price' ? "tab-strong" : "tab"}
            onClick={() => clickTab('price')}>
          Price
        </div>
        <div
            className={tab === 'mediaTrends' ? "tab-strong" : "tab"}
            onClick={() => {clickTab('mediaTrends')}}>
          Media Trends
        </div>
      </div>
      {tab === 'price' && <Price/>}
      {tab === 'mediaTrends' && <div className="App-mediaTrends">
        <BestNews />
        <Chart />
      </div>}
    </div>
  );
}

export default App;
