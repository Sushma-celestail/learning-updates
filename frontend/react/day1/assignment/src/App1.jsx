import React from 'react'
import Lists from './components/Lists'
import NameLists from './components/NameList'
import "./appStyles.css";
import styles from "./appStyles.module.css";


function App1() {
  return (
    <div>
      <h1 className="error">ERROR</h1>
      <h2 className={styles.success}>SUCCESS</h2>
    </div>
  )
}

export default App1