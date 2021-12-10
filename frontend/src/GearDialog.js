import React, { useEffect, useState } from "react";
import {
  Button,
  Link,
  Box,
  Dialog,
  DialogTitle,
  DialogContentText,
  DialogActions,
  DialogContent,
  TextField,
  FormControl,
  MenuItem,
  InputLabel,
  Select,
  InputAdornment,
} from "@mui/material";
import { useRef } from "react";

const GearDialog = ({ open, setOpen, user }) => {
  const [gears, setGears] = useState([]);
  const [selectedGear, setSelectedGear] = useState(null);

  const lifespanRef = useRef(null);
  const valueRef = useRef(null);
  const savingsRef = useRef(null);

  useEffect(() => {
    if (open) {
      fetch("/gear_by_user/" + user)
        .then((o) => o.json())
        .then((o) => setGears(o));
    }
  }, [user, open]);

  const handleClose = () => setOpen(false);
  const handleSubmit = () => {
    if (selectedGear) {
      fetch("/gear/add/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id: selectedGear.id,
          name: selectedGear.name,
          distance: selectedGear.converted_distance,
          lifespan: parseFloat(lifespanRef.current.value),
          value: parseFloat(valueRef.current.value),
          savings: parseFloat(savingsRef.current.value),
          user: user
        }),
      }).then(() => {
        setSelectedGear(null)
        handleClose()
      });
    }
  };

  const handleChange = (event) => {
    setSelectedGear(gears.find((x) => x.id === event.target.value));
  };

  return (
    <Dialog open={open}>
      <DialogTitle>Add Gear</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Add gear that you want to save for
        </DialogContentText>
        <FormControl sx={{ m: 1, width: "25ch" }}>
          <InputLabel id="gear-select-label">Pair</InputLabel>
          <Select
            labelId="gear-select-label"
            id="gear-select"
            value={selectedGear && selectedGear.id}
            label="Gear"
            onChange={handleChange}
          >
            {gears.map((g) => {
              return <MenuItem value={g.id}>{g.name}</MenuItem>;
            })}
          </Select>
        </FormControl>
        {selectedGear && (
          <>
            <Box
              component="form"
              sx={{
                "& > :not(style)": { m: 1, width: "25ch" },
              }}
              noValidate
              autoComplete="off"
            >
              <TextField
                label="Distance"
                variant="outlined"
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">km</InputAdornment>
                  ),
                }}
                value={selectedGear.converted_distance}
              />
              <TextField
                label="Lifespan"
                variant="outlined"
                inputRef={lifespanRef}
                type="number"
                defaultValue={800}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">km</InputAdornment>
                  ),
                }}
              />
              <TextField
                label="Value"
                inputRef={valueRef}
                defaultValue={1000}
                type="number"
                variant="outlined"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">R</InputAdornment>
                  ),
                }}
              />
              <TextField
                label="Savings"
                inputRef={savingsRef}
                type="number"
                variant="outlined"
                defaultValue={0}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">R</InputAdornment>
                  ),
                }}
              />
            </Box>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSubmit}>Add</Button>
      </DialogActions>
    </Dialog>
  );
};

export default GearDialog;


// await fetch("http://localhost:8000/gear/add", {
//     "credentials": "omit",
//     "headers": {
//         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
//         "Accept": "*/*",
//         "Accept-Language": "en-US,en;q=0.5",
//         "Content-Type": "application/json",
//         "Sec-Fetch-Dest": "empty",
//         "Sec-Fetch-Mode": "cors",
//         "Sec-Fetch-Site": "cross-site"
//     },
//     "referrer": "http://localhost:3000/",
//     "body": "{\"id\":\"g7720323\",\"name\":\"T-Rockets Yeti X\",\"distance\":490.3,\"lifespan\":\"700\",\"value\":\"1500\",\"savings\":\"0\"}",
//     "method": "POST",
//     "mode": "cors"
// });