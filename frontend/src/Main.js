import {
  Button,
  Box,
  List,
  ListItem,
  ListItemText,
  Typography,
  Paper,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import InvestecSecrets from "./InvestecSecrets";
import GearDialog from "./GearDialog";

const Main = ({ user }) => {
  const [userData, setUserData] = useState(null);
  const [openInvestec, setOpenInvestec] = useState(false);
  const [openGear, setOpenGear] = useState(false);
  const [shoes, setShoes] = useState([]);
  const [refresh, setRefresh] = useState(0);

  useEffect(() => {
    fetch("/user/" + user)
      .then((response) => response.json())
      .then((o) => setUserData(o))
  }, [user]);

  useEffect(() => {
    user &&
      fetch("/shoes/" + user).then((o) => o.json().then((o) => setShoes(o)));
  }, [user, openGear, refresh]);

  const stravaLinked = userData && userData.refresh_token;
  const investecLinked = userData && userData.investec;

  return (
    <Box sx={{ m: 2 }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Typography>Welcome {user}</Typography>
        <Box>
          <Button
            sx={{ m: 1 }}
            variant="outlined"
            href={"http://localhost:8000/strava/auth/" + user}
          >
            Link Strava Account
          </Button>
          <Button
            sx={{ m: 1 }}
            variant="outlined"
            onClick={() => setOpenInvestec(true)}
          >
            Link Investec Account
          </Button>
          <InvestecSecrets
            open={openInvestec}
            setOpen={setOpenInvestec}
            user={user}
          />
          <GearDialog
            user={user}
            open={openGear}
            setOpen={setOpenGear}
          ></GearDialog>
        </Box>
      </Box>
      <Typography variant="h3">Gear</Typography>
      <List sx={{ width: "100%", maxWidth: 500, bgcolor: "background.paper" }}>
        {shoes.map((o) => (
          <ListItem alignItems="flex-start" component={Paper} sx={{ m: 1 }} key={o.id}>
            <ListItemText
              primary={o.name}
              secondary={
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "row",
                    justifyContent: "space-between",
                  }}
                >
                  <div>
                    <div>Lifespan</div>
                    <div>{o.lifespan} km</div>
                  </div>
                  <div>
                    <div>Distance</div>
                    <div>{o.distance} km</div>
                  </div>
                  <div>
                    <div>Value</div>
                    <div>R{o.value}</div>
                  </div>
                  <div>
                    <div>Savings</div>
                    <div>R{o.savings}</div>
                  </div>
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>
      <Button onClick={() => setOpenGear(true)}>Add Gear</Button>
      <Button onClick={() => setRefresh(refresh + 1)}>Refresh</Button>
      <Typography variant="h3">History</Typography>
    </Box>
  );
};

export default Main;
