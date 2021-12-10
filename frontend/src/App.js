import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import Login from "./Login";
import Main from "./Main";

// const startStravaAuth = async () => {
//   try {
//     await fetch("/strava/auth");
//   } catch (err) {
//     console.log(err)
//   }
// };

function App() {
  const [username, setUsername] = useState("");

  // if (!username) {
  //   return <Login setUser={setUsername} />;
  // }

  return (
    <>{username ? <Main user={username} /> : <Login setUser={setUsername} /> }</>
  );
}

export default App;
