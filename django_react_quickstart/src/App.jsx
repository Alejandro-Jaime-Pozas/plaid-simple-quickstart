import React, { useState, useEffect, useCallback } from "react";
import { usePlaidLink } from "react-plaid-link";
import "./App.scss";

function App(props) {
  const [token, setToken] = useState(null);
  const [data, setData] = useState(null);
  const [latestTransactions, setLatestTransactions] = useState(null);
  const [loading, setLoading] = useState(true);

  const onSuccess = useCallback(async (publicToken) => {
    setLoading(true);
    await fetch("/api/exchange_public_token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ public_token: publicToken }),
    });
    await getLatestTransactions();
    await getBalance();
  }, []);

  // Creates a Link token
  const createLinkToken = useCallback(async () => {
    // For OAuth, use previously generated Link token
    if (window.location.href.includes("?oauth_state_id=")) {
      console.log('OAuth is included in the url, will proceed with OAuth process for creating link token.')
      const linkToken = localStorage.getItem('link_token');
      setToken(linkToken);
    } else {
      console.log('Fetching link token from backend, which fetches from plaid.');
      const response = await fetch("/api/create_link_token/", {});
      const data = await response.json();
      setToken(data.link_token);
      localStorage.setItem("link_token", data.link_token);
      console.log(`Link token successfully fetched and created: ${data.link_token}`);
    }
  }, [setToken]);

  // Fetch balance data
  const getBalance = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/balance/", {});
    const data = await response.json();
    setData(data);
    setLoading(false);
  }, [setData, setLoading]);

  // Fetch transaction data
  const getLatestTransactions = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/get_latest_transactions/", {});
    const data = await response.json();
    setLatestTransactions(data.latest_transactions);
    setLoading(false);
    console.log(data.latest_transactions);
  }, [setLatestTransactions, setLoading]);

  let isOauth = false;

  const config = {
    token,
    onSuccess,
  };

  // For OAuth, configure the received redirect URI
  if (window.location.href.includes("?oauth_state_id=")) {
    config.receivedRedirectUri = window.location.href;
    isOauth = true;
  }
  const { open, ready } = usePlaidLink(config);  // why is this function never called anywhere else?

  // need to understand this below
  useEffect(() => {
    if (token == null) {
      console.log('No token, will create one now.')
      createLinkToken();
    }
    if (isOauth && ready) {
      open();
    }
  }, [token, isOauth, ready, open]);

  return (
    <div>
      <button onClick={() => open()
        } disabled={!ready}>
        <strong>Link account</strong>
      </button>

      {/* if transaction data has been retreived successfully, show data */}
      {/* try displaying the transactions as I want them.
        merchant logo
        merchant name
        amount
        date
        (if there is some sort of description about the product purchase, ideal) */}
      {!loading &&
        latestTransactions != null &&
        latestTransactions.map((entry, i) => (
          <pre className="row lead" key={i}>
            <img className='img-fluid col-2 rounded ' src={entry.personal_finance_category_icon_url} alt="" />
            <div className="div">{entry.name}</div>
            <div className="div">{entry.merchant_name}</div>
            <div className="div">{entry.amount}</div>
            {/* <div>{JSON.stringify(entry[1], null, 2)}</div> */}
          </pre>
        )
      )}
      {/* if balance data has been retreived successfully, show data */}
      {/* {!loading &&
        data != null &&
        Object.entries(data).map((entry, i) => (
          <pre key={i}>
            <code>{JSON.stringify(entry[1], null, 2)}</code>
          </pre>
        )
      )} */}
    </div>
  );
}

export default App;
