// Form elements
const form = document.getElementById("paymentForm")
const cardholderNameInput = document.getElementById("cardholderName")
const cardNumberInput = document.getElementById("cardNumber")
const expiryMonthInput = document.getElementById("expiryMonth")
const expiryYearInput = document.getElementById("expiryYear")
const cvvInput = document.getElementById("cvv")

// Error message elements
const nameError = document.getElementById("nameError")
const cardError = document.getElementById("cardError")
const dateError = document.getElementById("dateError")
const cvvError = document.getElementById("cvvError")

// Format card number with spaces
cardNumberInput.addEventListener("input", (e) => {
  const value = e.target.value.replace(/\s/g, "")
  const formattedValue = value.replace(/(\d{4})/g, "$1 ").trim()
  e.target.value = formattedValue
  validateCardNumber()
})

// Format CVV (only numbers)
cvvInput.addEventListener("input", (e) => {
  e.target.value = e.target.value.replace(/\D/g, "")
  validateCVV()
})

// Validate cardholder name
cardholderNameInput.addEventListener("blur", validateCardholderName)
cardholderNameInput.addEventListener("input", () => {
  if (nameError.textContent) validateCardholderName()
})

// Validate expiry date
expiryMonthInput.addEventListener("blur", validateExpiryDate)
expiryYearInput.addEventListener("blur", validateExpiryDate)
expiryMonthInput.addEventListener("input", () => {
  if (dateError.textContent) validateExpiryDate()
})
expiryYearInput.addEventListener("input", () => {
  if (dateError.textContent) validateExpiryDate()
})

// Validation functions
function validateCardholderName() {
  const value = cardholderNameInput.value.trim()
  if (!value) {
    nameError.textContent = "El nombre del titular es requerido"
    return false
  }
  if (value.length < 3) {
    nameError.textContent = "El nombre debe tener al menos 3 caracteres"
    return false
  }
  if (!/^[a-zA-Z\s]+$/.test(value)) {
    nameError.textContent = "El nombre solo puede contener letras"
    return false
  }
  nameError.textContent = ""
  return true
}

function validateCardNumber() {
  const value = cardNumberInput.value.replace(/\s/g, "")
  if (!value) {
    cardError.textContent = "El número de tarjeta es requerido"
    return false
  }
  if (value.length !== 16) {
    cardError.textContent = "El número de tarjeta debe tener 16 dígitos"
    return false
  }
  if (!/^\d+$/.test(value)) {
    cardError.textContent = "El número de tarjeta solo puede contener dígitos"
    return false
  }
  if (!luhnCheck(value)) {
    cardError.textContent = "El número de tarjeta no es válido"
    return false
  }
  cardError.textContent = ""
  return true
}

function validateExpiryDate() {
  const month = Number.parseInt(expiryMonthInput.value)
  const year = Number.parseInt(expiryYearInput.value)

  if (!month || !year) {
    dateError.textContent = "La fecha de expiración es requerida"
    return false
  }

  if (month < 1 || month > 12) {
    dateError.textContent = "El mes debe estar entre 01 y 12"
    return false
  }

  const currentDate = new Date()
  const currentYear = currentDate.getFullYear()
  const currentMonth = currentDate.getMonth() + 1

  if (year < currentYear || (year === currentYear && month < currentMonth)) {
    dateError.textContent = "La tarjeta ha expirado"
    return false
  }

  dateError.textContent = ""
  return true
}

function validateCVV() {
  const value = cvvInput.value
  if (!value) {
    cvvError.textContent = "El código de seguridad es requerido"
    return false
  }
  if (value.length < 3 || value.length > 4) {
    cvvError.textContent = "El código debe tener 3 o 4 dígitos"
    return false
  }
  if (!/^\d+$/.test(value)) {
    cvvError.textContent = "El código solo puede contener dígitos"
    return false
  }
  cvvError.textContent = ""
  return true
}

// Luhn algorithm for card validation
function luhnCheck(cardNumber) {
  let sum = 0
  let isEven = false

  for (let i = cardNumber.length - 1; i >= 0; i--) {
    let digit = Number.parseInt(cardNumber[i])

    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit -= 9
      }
    }

    sum += digit
    isEven = !isEven
  }

  return sum % 10 === 0
}

// Form submission
form.addEventListener("submit", (e) => {
  e.preventDefault()

  // Validate all fields
  const isNameValid = validateCardholderName()
  const isCardValid = validateCardNumber()
  const isDateValid = validateExpiryDate()
  const isCVVValid = validateCVV()

  if (isNameValid && isCardValid && isDateValid && isCVVValid) {
    alert("Formulario válido. Procesando pago...")
    console.log("Datos del formulario:", {
      cardholderName: cardholderNameInput.value,
      cardNumber: cardNumberInput.value.replace(/\s/g, ""),
      expiryMonth: expiryMonthInput.value,
      expiryYear: expiryYearInput.value,
      cvv: cvvInput.value,
    })
    // Aquí iría la lógica para enviar los datos al servidor
  }
})
