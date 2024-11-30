import React, {createContext} from 'react';
import './App.css';
import Price from "./Price/Price";
import Chart from "./MediaTrends/Chart";
import BestNews from "./MediaTrends/BestNews";
import News from "./Price/News";
import {useState} from "react";

interface ContextType {
  showPop: string | undefined;
  setShowPop: React.Dispatch<React.SetStateAction<string | undefined>>;
}

const Context = createContext<ContextType | undefined>(undefined);

function App() {
  const [tab, setTab] = useState<string>('price');
  const [showPop, setShowPop] = useState<string | undefined>(undefined);

  const clickTab = (tabName: string) => {
    if (tab !== tabName) {
      setTab(tabName);
    }
  }

  return (
    <Context.Provider value={{ showPop, setShowPop }}>
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
      {tab === 'price' && showPop && <News crypto={showPop}/>}
      {tab === 'mediaTrends' && <div className="App-mediaTrends">
        <BestNews />
        <Chart />
      </div>}
    </Context.Provider>
  );
}

export {Context};
export default App;
