// Initialize all input of type date
const loader = document.getElementById("loader");
const info_text = document.querySelector("#available-sites p");
const cols = document.querySelector("#available-sites .columns");
const stripe = Stripe(stripe_key);
var calendars = bulmaCalendar.attach('[type="date"]', {
  isRange: true,
  color: "success",
  showButtons: false,
  labelFrom: "Arrival date",
  labelTo: "Departure date",
  minDate: new Date(),
  allowSameDayRange: false,
  headerPosition: "bottom",
  dateFormat: "YYYY-MM-DD",
});

const getAvailableSites = async (url = "") => {
  // Default options are marked with *
  const response = await fetch(url, {
    method: "GET",
    mode: "cors", 
    cache: "no-cache", 
    credentials: "same-origin", 
  });
  return response.json(); 
};

var SELECTED_SITE_ID;
var PRICE;
var step = 1;

const selectSite = (e) => {
  e.innerHTML = "Selected";
  document.querySelectorAll(".select-btn").forEach((btn) => {
    if (btn != e) {
      btn.innerHTML = "Select";
    }
  });
  SELECTED_SITE_ID = e.dataset.siteid;
  PRICE = e.dataset.price;
};

const next = document.getElementById("next");
    previous = document.getElementById("previous"),
    step_segments = document.querySelectorAll(".steps-segment"),
    pay = document.getElementById('pay'),
    first_name = document.getElementById("first_name"),
    last_name = document.getElementById("last_name"),
    email = document.getElementById("email"),
    phone_number = document.getElementById("phone_number"),
    info = document.getElementById("info");
var arrival_date;
var departure_date;

next.addEventListener("click", () => {
  const current_step = document.querySelector(`#step-${step}`);
  switch (step) {
    case 1:
      if (!SELECTED_SITE_ID) {
        alert("Please select a site.");
        return false;
      }
      break;
    case 2:
      console.log("step 2");
      const inputs = current_step.querySelectorAll("input");
      var not_finished;
      // check if all inputs are filled in
      inputs.forEach((i) => {
        const help_dangers = i.parentElement.parentElement.querySelectorAll(
          ".help.is-danger"
        );
        console.log(help_dangers);
        help_dangers.forEach((text) => {
          text.remove();
        });
        if (i.value.length == 0) {
          i.classList.add("is-danger");
          i.parentElement.parentElement.innerHTML +=
            '<p class="help is-danger">This field is required.</p>';
          not_finished = true;
        } else {
          i.classList.remove("is-danger");
        }
      });
      if (not_finished) return false;
    case 3:
      info.innerHTML = `
            <p><strong>First Name:</strong> ${first_name.value}</p>
            <p><strong>Last Name:</strong> ${last_name.value}</p>
            <p><strong>Email:</strong> ${email.value}</p>
            <p><strong>Phone Number:</strong> ${phone_number.value}</p>
            <p><strong>Site ID:</strong> ${SELECTED_SITE_ID}</p>
            <h3>Price before tax:</strong> ${PRICE}</h3>
            `;
        
    default:
      break;
  }
  current_step.style.display = "none";
  const next_step = document.querySelector(`#step-${step + 1}`);
  next_step.style.display = "block";
  step++;
  if (step > 1) {
    previous.style.display = "block";
  }
  if (step == 3) {
    next.style.display = "none";
    pay.style.display = "block";
  }
  step_segments[step - 1].classList.toggle("is-active");
  step_segments[step - 2].classList.toggle("is-active");
});

previous.addEventListener("click", () => {
  const current_step = document.querySelector(`#step-${step}`);
  current_step.style.display = "none";
  const previous_step = document.querySelector(`#step-${step - 1}`);
  previous_step.style.display = "block";
  step_segments[step - 2].classList.add("is-active");
  step_segments[step - 1].classList.remove("is-active");
  console.log(step_segments[step]);
  step--;
  if (step == 1) {
    previous.style.display = "none";
  }
  if (step < 3) {
    next.style.display = "block";
    pay.style.display = "none";
  }
});

pay.addEventListener('click', () => {
    pay.classList.add('is-loading');
    previous.setAttribute('disabled', true);
    fetch(location.origin + '/api/reservation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'site_id': parseInt(SELECTED_SITE_ID),
            'first_name': first_name.value,
            'last_name': last_name.value,
            'arrival_date': arrival_date,
            'departure_date': departure_date,
            'email': email.value,
        })
    }).then(function(r) {
        console.log(r);
        return r.json();
    }).then(function(resp) {
        const sessionId = resp.stripe_session_id;
        stripe.redirectToCheckout({
            sessionId: sessionId
        });
    });
})

// Loop on each calendar initialized
for (var i = 0; i < calendars.length; i++) {
  // Add listener to select event
  calendars[i].on("select", (date) => {
    console.log("selected");
    const value = date.data.value().split(" - ");
    arrival_date = value[0];
    departure_date = value[1];
    info_text.style.display = "none";
    loader.style.display = "block";
    cols.innerHTML = "";
    cols.style.display = "none";
    date.data.hide();
    setTimeout(() => {
      getAvailableSites(
        location.origin +
          `/api/get-available-sites?arrival_date=${arrival_date}&departure_date=${departure_date}`
      )
        .then((data) => {
          console.log(data.available_sites.length);
          if (data.available_sites.length == 0) {
            info_text.innerHTML =
              "We couldn't find any sites available for the date range you selected. Please choose another date.";
          } else {
            cols.style.display = "flex";
            data.available_sites.forEach((site) => {
              cols.innerHTML += `<div class="column is-one-fifth">
                                        <div class="card">
                                            <div class="card-image">
                                            <figure class="image is-4by3">
                                                <img src="/static/images/hero_img.jpg" alt="Placeholder image">
                                            </figure>
                                            </div>
                                            <div class="card-content has-text-centered">
                                                <p class="title is-4">${
                                                  site.name
                                                }</p>
                                                <p class="subtitle is-6 has-text-success">Available</p>
                                                <p class="subtitle is-6">Before Tax: <strong>$${(
                                                  35 * data.delta
                                                ).toLocaleString()}</strong></p>
                                        
                                                <div class="content">
                                                    $35/night
                                                </div>
                                                <footer class="card-footer">
                                                    <div class="card-footer-item">
                                                        <button class="button is-primary select-btn" onclick="selectSite(this)" data-siteid="${
                                                          site.id
                                                        }" data-price="$${35 * data.delta}">Select</button>
                                                    </div>
                                                </footer>
                                            </div>
                                        </div>
                                    </div>`;
            });
            info_text.innerHTML = `Found ${data.available_sites.length} sites.`;
          }
        })
        .finally(() => {
          info_text.style.display = "block";
          loader.style.display = "none";
          location.hash = "#available-sites-header";
        })
        .catch((e) => {
          console.log(e);
          info_text.innerHTML =
            "An unexpected error occurred while processing your request. Please try again later or call us at (555) 555-5555. We're sorry for any inconvenience.";
        });
    }, 500);
  });
}
