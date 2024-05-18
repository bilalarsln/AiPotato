const navMenu=document.getElementById("nav-menu"),navToggle=document.getElementById("nav-toggle"),navClose=document.getElementById("nav-close");navToggle&&navToggle.addEventListener("click",()=>{navMenu.classList.add("show-menu")}),navClose&&navClose.addEventListener("click",()=>{navMenu.classList.remove("show-menu")});const navLink=document.querySelectorAll(".nav__link");function linkAction(){const a=document.getElementById("nav-menu");a.classList.remove("show-menu")}navLink.forEach(a=>a.addEventListener("click",linkAction));function scrollHeader(){const a=document.getElementById("header");80<=this.scrollY?a.classList.add("scroll-header"):a.classList.remove("scroll-header")}window.addEventListener("scroll",scrollHeader);const accordionItems=document.querySelectorAll(".questions__item");accordionItems.forEach(a=>{const b=a.querySelector(".questions__header");b.addEventListener("click",()=>{const b=document.querySelector(".accordion-open");toggleItem(a),b&&b!==a&&toggleItem(b)})});const toggleItem=a=>{const b=a.querySelector(".questions__content");a.classList.contains("accordion-open")?(b.removeAttribute("style"),a.classList.remove("accordion-open")):(b.style.height=b.scrollHeight+"px",a.classList.add("accordion-open"))},sections=document.querySelectorAll("section[id]");function scrollActive(){const a=window.pageYOffset;sections.forEach(b=>{const c=b.offsetHeight,d=b.offsetTop-58,e=b.getAttribute("id");a>d&&a<=d+c?document.querySelector(".nav__menu a[href*="+e+"]").classList.add("active-link"):document.querySelector(".nav__menu a[href*="+e+"]").classList.remove("active-link")})}window.addEventListener("scroll",scrollActive);function scrollUp(){const a=document.getElementById("scroll-up");400<=this.scrollY?a.classList.add("show-scroll"):a.classList.remove("show-scroll")}window.addEventListener("scroll",scrollUp);const themeButton=document.getElementById("theme-button"),darkTheme="dark-theme",iconTheme="ri-sun-line",selectedTheme=localStorage.getItem("selected-theme"),selectedIcon=localStorage.getItem("selected-icon"),getCurrentTheme=()=>document.body.classList.contains(darkTheme)?"dark":"light",getCurrentIcon=()=>themeButton.classList.contains(iconTheme)?"ri-moon-line":"ri-sun-line";selectedTheme&&(document.body.classList["dark"===selectedTheme?"add":"remove"](darkTheme),themeButton.classList["ri-moon-line"===selectedIcon?"add":"remove"](iconTheme)),themeButton.addEventListener("click",()=>{document.body.classList.toggle(darkTheme),themeButton.classList.toggle(iconTheme),localStorage.setItem("selected-theme",getCurrentTheme()),localStorage.setItem("selected-icon",getCurrentIcon())});const sr=ScrollReveal({origin:"top",distance:"60px",duration:2500,delay:400});sr.reveal(`.home__data`),sr.reveal(`.home__img`,{delay:500}),sr.reveal(`.home__social`,{delay:600}),sr.reveal(`.about__img, .contact__box`,{origin:"left"}),sr.reveal(`.about__data, .contact__form`,{origin:"right"}),sr.reveal(`.steps__card, .product__card, .questions__group, .footer`,{interval:100});

function dropHandler(ev) {
    console.log("File(s) dropped");
  
    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();
  
    if (ev.dataTransfer.items) {
      // Use DataTransferItemList interface to access the file(s)
      [...ev.dataTransfer.items].forEach((item, i) => {
        // If dropped items aren't files, reject them
        if (item.kind === "file") {
          const file = item.getAsFile();
          console.log(`… file[${i}].name = ${file.name}`);
        }
      });
    } else {
      // Use DataTransfer interface to access the file(s)
      [...ev.dataTransfer.files].forEach((file, i) => {
        console.log(`… file[${i}].name = ${file.name}`);
      });
    }
  }
  