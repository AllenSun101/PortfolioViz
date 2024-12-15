'use client'
import { useState, useEffect } from 'react';
import axios from 'axios';

import React from "react";
import {
    ComposedChart,
    Area,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    CartesianGrid,
    ResponsiveContainer,
} from "recharts";

export default function StockHistory(){
    const [stocks, setStocks] = useState([]);
    const [filteredStocks, setFilteredStocks] = useState(stocks);
    const [inputValue, setInputValue] = useState("");
    const [series, setSeries] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get("http://localhost:5000/get_traded_tickers");
                setStocks(response.data.tickers);
                setFilteredStocks(response.data.tickers);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData();
    }, []);

    const handleOptionClick = async (ticker) => {
        const response = await axios.get("http://localhost:5000/get_shares_over_time", {
            params: {
                ticker: ticker,
            }
        });
        setSeries(response.data.data);
        setInputValue(ticker);
        setFilteredStocks(stocks);
    };

    const handleInputChange = (e) => {
        const value = e.target.value;
        setInputValue(value);
        setFilteredStocks(
            stocks.filter((ticker) =>
                ticker.replace(/[^a-zA-Z]/g, '').toLowerCase().includes(value.replace(/[^a-zA-Z]/g, '').toLowerCase())
            )
        );
    };

    return(
        <div className='bg-white py-24 px-8 sm:px-16'>
            <h1 className='text-4xl text-center mb-6 font-semibold'>Position History</h1>
            <div className='text-center mb-12'>
                <span className='mr-4 text-xl'>Ticker: </span>
                <span>
                    <input
                        type="text"
                        value={inputValue}
                        onChange={handleInputChange}
                        placeholder="Enter Ticker..."
                        className="border rounded rounded-xl p-2"
                    />
                    <ul className="border rounded max-h-40 overflow-y-auto mt-2 w-1/4 mx-auto">
                        {filteredStocks.map((option, index) => (
                            <li key={index} className="p-2 hover:bg-gray-200 cursor-pointer text-md"
                            onClick={() => handleOptionClick(option)}>
                                {option}
                            </li>
                        ))}
                    </ul>
                </span>
            </div>

        <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={series}>
                {/* X-Axis */}
                <XAxis dataKey="Date" />
                {/* Y-Axis for Shares */}
                <YAxis yAxisId="left" label={{ value: "Shares", angle: -90, position: "insideLeft" }} />
                {/* Y-Axis for Price */}
                <YAxis
                    yAxisId="right"
                    orientation="right"
                    label={{ value: "Price", angle: -90, position: "insideRight" }}
                    domain={['auto', 'auto']}
                />
                {/* Grid */}
                <CartesianGrid strokeDasharray="3 3" />
                {/* Tooltip */}
                <Tooltip />
                {/* Legend */}
                <Legend />
                {/* Area Chart for Price */}
                <Area
                    yAxisId="right"
                    type="monotone"
                    dataKey="Price"
                    fill="purple"
                    stroke="purple"
                    strokeWidth={2}
                    fillOpacity={0.3} // Add transparency
                    baseValue="dataMin"
                />
                {/* Line Chart for Shares */}
                <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="Shares"
                    stroke="#8884d8"
                    strokeWidth={3}
                />
            </ComposedChart>
        </ResponsiveContainer>


        </div>
    );
}