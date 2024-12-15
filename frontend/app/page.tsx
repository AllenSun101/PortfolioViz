'use client'

import Image from "next/image";
import axios from "axios";
import { useState, useEffect } from "react";

export default function Home() {
  const [date, setDate] = useState("");
  const [data, setData] = useState([]);
  const columnOrder = ["Stock", "Price", "Shares", "Total_Value", "Percentage_of_Fund"];

  useEffect(() => {
    const fetchData = async () => {
        try {
          const dateResponse = await axios.get("http://localhost:5000/get_date");
          setDate(dateResponse.data.date);

          const response = await axios.get("http://localhost:5000/get_portfolio");
          setData(response.data.data);
        } catch (error) {
          console.error("Error fetching data:", error);
        }
    };

    fetchData();
  }, []);

  return (
    <div className="bg-white py-24 px-8 sm:px-16">
      <div className="text-4xl text-center mb-2 font-semibold">
        <h1>Current Holdings</h1>
      </div>
      <div className="text-xl text-center mb-6">
        <p>As of {date}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="table-auto border-collapse border border-gray-300 w-3/4 mx-auto">
          <thead>
            <tr className="bg-gray-200">
              <th className="border border-gray-300 px-4 py-2">Ticker</th>
              <th className="border border-gray-300 px-4 py-2">Price</th>
              <th className="border border-gray-300 px-4 py-2">Shares</th>
              <th className="border border-gray-300 px-4 py-2">Total Value</th>
              <th className="border border-gray-300 px-4 py-2">Percentage of Fund</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row: any, rowIndex: any) => (
              <tr
                key={rowIndex}
                className={rowIndex % 2 === 0 ? "bg-white" : "bg-gray-100"}
              >
                {columnOrder.map((colKey, colIndex) => (
                  <td key={colIndex} className="px-4 py-2 border border-gray-300 text-center">
                    {row[colKey]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length < 10? <div className="mb-80"></div>: <div></div>}
    </div>
  );
}
