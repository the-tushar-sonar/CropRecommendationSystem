document.addEventListener("DOMContentLoaded", () => {
  // Page navigation elements
  const welcomeScreen = document.getElementById("welcome-screen")
  const inputForm = document.getElementById("input-form")
  const resultsPage = document.getElementById("results")

  // Buttons
  const getStartedBtn = document.getElementById("get-started-btn")
  const backToWelcomeBtn = document.getElementById("back-to-welcome")
  const backToFormBtn = document.getElementById("back-to-form")
  const newPredictionBtn = document.getElementById("new-prediction")

  // Form elements
  const cropForm = document.getElementById("crop-form")
  const formInputs = cropForm.querySelectorAll("input")

  // Check if we have a result and should show the results page
  const resultMessage = document.querySelector(".result-message")
  if (resultMessage && resultMessage.textContent.trim() !== "") {
    showPage(resultsPage)
    updateCropImage(resultMessage.textContent)
  }

  // Page navigation functions
  getStartedBtn.addEventListener("click", () => {
    showPage(formInputs.)
  })

  backToWelcomeBtn.addEventListener("click", () => {
    showPage(welcomeScreen)
  })

  backToFormBtn.addEventListener("click", () => {
    showPage(inputForm)
  })

  newPredictionBtn.addEventListener("click", () => {
    // Reset form
    cropForm.reset()
    showPage(inputForm)
  })

  // Form validation
  formInputs.forEach((input) => {
    input.addEventListener("input", function () {
      validateInput(this)
    })
  })

  cropForm.addEventListener("submit", function (e) {
    let isValid = true

    formInputs.forEach((input) => {
      if (!validateInput(input)) {
        isValid = false
      }
    })

    if (!isValid) {
      e.preventDefault()
    } else {
      // Add loading animation if needed
      const submitBtn = this.querySelector('button[type="submit"]')
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...'
      submitBtn.disabled = true
    }
  })

  // Helper functions
  function showPage(page) {
    // Hide all pages
    document.querySelectorAll(".page").forEach((p) => {
      p.classList.remove("active")
    })

    // Show the selected page
    page.classList.add("active")

    // Add animation classes
    const elements = page.querySelectorAll(".glass-card, h1, h2, p, .form-group, .btn")
    elements.forEach((el, index) => {
      el.style.animation = "none"
      el.offsetHeight // Trigger reflow
      el.style.animation = `fadeInUp 0.5s ease forwards ${index * 0.1}s`
    })
  }

  function validateInput(input) {
    const min = Number.parseFloat(input.min)
    const max = Number.parseFloat(input.max)
    const value = Number.parseFloat(input.value)

    // Remove any existing error message
    const existingError = input.parentNode.querySelector(".error-message")
    if (existingError) {
      existingError.remove()
    }

    // Check if empty
    if (input.value.trim() === "") {
      addErrorMessage(input, "This field is required")
      return false
    }

    // Check if within range
    if (value < min || value > max) {
      addErrorMessage(input, `Value must be between ${min} and ${max}`)
      return false
    }

    return true
  }

  function addErrorMessage(input, message) {
    const errorElement = document.createElement("span")
    errorElement.className = "error-message"
    errorElement.textContent = message
    input.parentNode.appendChild(errorElement)
  }

  function updateCropImage(resultText) {
    const cropImage = document.getElementById("crop-image")

    // Extract crop name from result text
    const cropMatch = resultText.match(/^(.*?) is the best crop/)
    if (cropMatch && cropMatch[1]) {
      const cropName = cropMatch[1].toLowerCase()

      // Set image based on crop name
      cropImage.src = `/static/images/crops/${cropName}.jpg`

      // Fallback if image doesn't exist
      cropImage.onerror = function () {
        this.src = "/static/images/crops/default.jpg"
      }
    }
  }

  // Add leaf animations
  function createLeaves() {
    const leafAnimation = document.querySelector(".leaf-animation")
    if (!leafAnimation) return

    const leafImages = [
      "/static/images/leaf1.png",
      "/static/images/leaf2.png",
      "/static/images/leaf3.png",
    ]

    // Add more leaves for background effect
    for (let i = 0; i < 5; i++) {
      const leaf = document.createElement("img")
      leaf.src = leafImages[Math.floor(Math.random() * leafImages.length)]
      leaf.className = "leaf"
      leaf.style.top = `${Math.random() * 100}%`
      leaf.style.left = `${Math.random() * 100}%`
      leaf.style.opacity = `${0.3 + Math.random() * 0.3}`
      leaf.style.transform = `scale(${0.5 + Math.random() * 0.5}) rotate(${Math.random() * 360}deg)`
      leaf.style.animation = `floatLeaf ${15 + Math.random() * 10}s infinite ease-in-out ${Math.random() * 5}s`

      leafAnimation.appendChild(leaf)
    }
  }

  createLeaves()
})

