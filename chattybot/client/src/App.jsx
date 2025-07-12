// src/App.js
import Navbar from './Navbar'

import React from 'react';
import ChatApp from './components/ChatApp';
import './App.css';

const App = () => {
  return (
    <div className="App">
      {/* <Navbar /> */}
      <ChatApp />
    </div>
  );
};

export default App;
