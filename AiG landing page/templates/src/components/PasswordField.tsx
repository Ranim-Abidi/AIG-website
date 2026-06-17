import { useState } from 'react'
import './FormComponents.css'

interface PasswordFieldProps {
  name?: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  error?: string
  disabled?: boolean
  required?: boolean
  placeholder?: string
}

export default function PasswordField({
  name = 'password',
  value,
  onChange,
  error,
  disabled = false,
  required = true,
  placeholder = 'Password',
}: PasswordFieldProps) {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div className="form-field">
      <div className="password-input-wrapper">
        <input
          type={showPassword ? 'text' : 'password'}
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`form-input ${error ? 'error' : ''}`}
          disabled={disabled}
          required={required}
          autoComplete="new-password"
        />
        <button
          type="button"
          className="password-toggle"
          onClick={() => setShowPassword((prev) => !prev)}
          disabled={disabled}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? 'Hide' : 'Show'}
        </button>
      </div>
      <span className="field-hint">
        Min 8 characters with uppercase, lowercase, and a number
      </span>
      {error && <span className="error-message">{error}</span>}
    </div>
  )
}
