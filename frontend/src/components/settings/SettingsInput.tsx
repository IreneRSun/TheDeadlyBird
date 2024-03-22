import { Form } from 'react-bootstrap';
import React from 'react';

import styles from "./SettingsInput.module.css";

type SettingsInputOptions = {
  title: string;
  name: string;
  type: "text"|"email"|"password";
  value: string;
  valueSetter?: React.Dispatch<React.SetStateAction<string>>;
  disabled?: boolean;
  placeholder?: string;
};

const SettingsInput: React.FC<SettingsInputOptions> = options => {
  /** Function for handling a change in the input */
  function onChange(event: React.ChangeEvent<HTMLInputElement>) {
    if (options.valueSetter) {
      options.valueSetter(event.target.value);
    }
  }

  /** Settings input */
  return (
    <Form.Group className={styles.container} data-bs-theme={"dark"}>
      <Form.Label className={styles.label}>
        {options.title}
      </Form.Label>
      <Form.Control
        type={options.type}
        as="input"
        className={styles.input}
        disabled={options.disabled}
        placeholder={options.placeholder}
        value={options.value}
        onChange={onChange}
      />
    </Form.Group>
  );
};

export default SettingsInput;