interface FormAlertsProps {
  success?: boolean
  error?: string | null
  successMessage?: string
}

export default function FormAlerts({
  success,
  error,
  successMessage = 'Application submitted successfully! Check your email for next steps.',
}: FormAlertsProps) {
  return (
    <>
      {success && (
        <div className="alert alert-success">
          <p>{successMessage}</p>
        </div>
      )}
      {error && (
        <div className="alert alert-error">
          <p>{error}</p>
        </div>
      )}
    </>
  )
}
