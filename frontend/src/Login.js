import React, { useState } from "react";
import TextField from "@mui/material/TextField";
import { Box, Button } from "@mui/material";

const Login = ({ setUser }) => {
  const [userValue, setUserValue] = useState("");

  return (
    <>
      <img src="/android-chrome-192x192.png" />
      <Box sx={{ display: "flex", alignItems: "center", m: 2 }}>
        <TextField
          id="username"
          label="Username"
          variant="outlined"
          value={userValue}
          onChange={(e) => setUserValue(e.target.value)}
        />
        <Button
          sx={{ p: 0, m: 2, height: "100%" }}
          variant="outlined"
          onClick={() => setUser(userValue)}
        >
          Enter
        </Button>
      </Box>
    </>
  );
};

export default Login;
