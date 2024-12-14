import Image from "next/image";

export default function Home() {
  var date = "2024-12-11";

  return (
    <div className="bg-white py-24 px-8 sm:px-16">
      <div className="text-4xl text-center mb-2 font-semibold">
        <h1>Current Holdings</h1>
      </div>
      <div className="text-xl text-center">
        <p>Today's date: {date}</p>
      </div>
      <div>
        <table className="">
          <tr>
            <th>Ticker</th>
            <th>Price</th>
            <th>Shares</th>
            <th>Total Value</th>
            <th>Percentage of Fund</th>
            <th>Cost Basis</th>
            <th>Profit/Loss</th>
          </tr>
        </table>
      </div>
    </div>
  );
}
