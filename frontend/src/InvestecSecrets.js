import React, { useState } from "react";
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
} from "@mui/material";
import { useRef } from "react";

const InvestecSecrets = ({ open, setOpen, user }) => {
  const idRef = useRef(null);
  const secretRef = useRef(null);
  const handleClose = () => setOpen(false);
  const handleSubmit = () => {
    fetch("/investec/auth/" + user, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: idRef.current.value,
        secret: secretRef.current.value,
      }),
    }).then(() => handleClose());
  };


  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Investec Details</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Enter your Investec Programmable Banking details.
        </DialogContentText>
        <TextField inputRef={idRef} label="id" />
        <TextField inputRef={secretRef} label="secret" type="password" />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSubmit}>Submit</Button>
      </DialogActions>
    </Dialog>
  );
};

export default InvestecSecrets;
