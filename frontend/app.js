// Éléments de la page
const vue = document.getElementById("vue");
const page = document.getElementById("page");
const ctx = page.getContext("2d");
const accueil = document.getElementById("accueil");
const barre = document.getElementById("barre");
const salonInfo = document.getElementById("salon-info");
const message = document.getElementById("message");
const champCode = document.getElementById("champ-code");
const champCouleur = document.getElementById("couleur");
const champTaille = document.getElementById("taille");

// Valeurs de réglage
const POINTS_PAR_TRAIT = 2000;
const TRAITS_PAR_REPONSE = 500;
const DELAI_RAFRAICHISSEMENT = 1000;

// État de l'application
let salon = null;
let outil = "pinceau";
let decalage = { x: 0, y: 0 };
let dernierId = 0;
let traitEnCours = null;
let deplacement = null;
let rafraichissementEnCours = false;

// Page blanche
ctx.fillStyle = "#ffffff";
ctx.fillRect(0, 0, page.width, page.height);

// Déplacement de la page dans la vue, sans sortir de la page
function placerPage() {
  const minX = Math.min(0, vue.clientWidth - page.width);
  const minY = Math.min(0, vue.clientHeight - page.height);
  decalage.x = Math.max(minX, Math.min(0, decalage.x));
  decalage.y = Math.max(minY, Math.min(0, decalage.y));
  page.style.transform = `translate(${decalage.x}px, ${decalage.y}px)`;
}

// On démarre au centre de la page
decalage.x = (vue.clientWidth - page.width) / 2;
decalage.y = (vue.clientHeight - page.height) / 2;
placerPage();
window.addEventListener("resize", placerPage);

// Position de la souris sur la page (et non sur l'écran)
function positionSurPage(evenement) {
  const rect = vue.getBoundingClientRect();
  return [
    evenement.clientX - rect.left - decalage.x,
    evenement.clientY - rect.top - decalage.y,
  ];
}

function appliquerStyle(trait) {
  ctx.strokeStyle = trait.couleur;
  ctx.fillStyle = trait.couleur;
  ctx.lineWidth = trait.taille;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
}

// Dessine un trait complet (utilisé pour les traits reçus du serveur)
function dessinerTrait(trait) {
  appliquerStyle(trait);
  const points = trait.points;
  if (points.length === 1) {
    ctx.beginPath();
    ctx.arc(points[0][0], points[0][1], trait.taille / 2, 0, Math.PI * 2);
    ctx.fill();
    return;
  }
  ctx.beginPath();
  ctx.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) {
    ctx.lineTo(points[i][0], points[i][1]);
  }
  ctx.stroke();
}

// Dessine seulement le dernier petit segment pendant que l'on dessine
function dessinerSegment(trait, depart, arrivee) {
  appliquerStyle(trait);
  ctx.beginPath();
  ctx.moveTo(depart[0], depart[1]);
  ctx.lineTo(arrivee[0], arrivee[1]);
  ctx.stroke();
}

function nouveauTrait(premierPoint) {
  return {
    // La gomme dessine en blanc
    couleur: outil === "gomme" ? "#ffffff" : champCouleur.value,
    taille: Number(champTaille.value),
    points: [premierPoint],
  };
}

async function envoyerTrait(trait) {
  try {
    await fetch(`/api/traits/${salon}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trait),
    });
  } catch (erreur) {
    // Le trait reste visible sur cette page même si l'envoi échoue
  }
}

// Souris et doigt : on utilise les "pointer events"
vue.addEventListener("pointerdown", (evenement) => {
  if (!salon) return;
  vue.setPointerCapture(evenement.pointerId);

  if (outil === "main") {
    deplacement = {
      x: evenement.clientX,
      y: evenement.clientY,
      depart: { x: decalage.x, y: decalage.y },
    };
    vue.style.cursor = "grabbing";
    return;
  }

  traitEnCours = nouveauTrait(positionSurPage(evenement));
  dessinerTrait(traitEnCours);
});

vue.addEventListener("pointermove", (evenement) => {
  if (deplacement) {
    decalage.x = deplacement.depart.x + evenement.clientX - deplacement.x;
    decalage.y = deplacement.depart.y + evenement.clientY - deplacement.y;
    placerPage();
    return;
  }

  if (!traitEnCours) return;
  const points = traitEnCours.points;
  const dernier = points[points.length - 1];
  const point = positionSurPage(evenement);
  dessinerSegment(traitEnCours, dernier, point);
  points.push(point);

  // Un trait trop long est coupé en plusieurs morceaux
  if (points.length >= POINTS_PAR_TRAIT) {
    envoyerTrait(traitEnCours);
    traitEnCours = nouveauTrait(point);
  }
});

function finirAction() {
  if (deplacement) {
    deplacement = null;
    vue.style.cursor = "";
  }
  if (traitEnCours) {
    envoyerTrait(traitEnCours);
    traitEnCours = null;
  }
}
vue.addEventListener("pointerup", finirAction);
vue.addEventListener("pointercancel", finirAction);

// Choix de l'outil
document.querySelectorAll("[data-outil]").forEach((bouton) => {
  bouton.addEventListener("click", () => {
    outil = bouton.dataset.outil;
    document.querySelectorAll("[data-outil]").forEach((b) => b.classList.remove("actif"));
    bouton.classList.add("actif");
    vue.className = `outil-${outil}`;
  });
});

// Récupère les nouveaux traits dessinés par les autres (et par nous)
async function rafraichir() {
  if (rafraichissementEnCours || !salon) return;
  rafraichissementEnCours = true;
  try {
    let encore = true;
    while (encore) {
      const reponse = await fetch(`/api/traits/${salon}?apres=${dernierId}`);
      if (!reponse.ok) break;
      const traits = await reponse.json();
      for (const trait of traits) {
        dessinerTrait(trait);
        dernierId = trait.id;
      }
      encore = traits.length === TRAITS_PAR_REPONSE;
    }
  } catch (erreur) {
    // On réessaiera au prochain rafraîchissement
  } finally {
    rafraichissementEnCours = false;
  }
}

async function entrerDansSalon(code) {
  salon = code;
  accueil.hidden = true;
  barre.hidden = false;
  salonInfo.textContent = `Salon : ${code}`;
  await rafraichir();
  setInterval(rafraichir, DELAI_RAFRAICHISSEMENT);
}

// Écran d'accueil
document.getElementById("btn-creer").addEventListener("click", async () => {
  message.textContent = "";
  try {
    const reponse = await fetch("/api/salons", { method: "POST" });
    if (!reponse.ok) throw new Error();
    const donnees = await reponse.json();
    entrerDansSalon(donnees.code);
  } catch (erreur) {
    message.textContent = "Impossible de créer le salon.";
  }
});

document.getElementById("btn-rejoindre").addEventListener("click", async () => {
  message.textContent = "";
  const code = champCode.value.trim().toUpperCase();
  if (!code) {
    message.textContent = "Entre le code du salon.";
    return;
  }
  try {
    const reponse = await fetch(`/api/salons/${encodeURIComponent(code)}`);
    if (reponse.status === 404) {
      message.textContent = "Salon introuvable.";
      return;
    }
    if (!reponse.ok) throw new Error();
    entrerDansSalon(code);
  } catch (erreur) {
    message.textContent = "Impossible de rejoindre le salon.";
  }
});
