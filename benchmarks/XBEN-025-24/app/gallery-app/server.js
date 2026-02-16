"use strict";

const express = require("express");
const exphbs = require("express-handlebars");
const session = require("express-session");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 80;

const hbs = exphbs.create({
	defaultLayout: "main",
	extname: ".hbs",
	layoutsDir: path.join(__dirname, "views/layouts/"),
	helpers: {
		currency: function (val) {
			return parseFloat(val).toFixed(2);
		},
		eq: function (a, b) {
			return a === b;
		},
		year: function () {
			return new Date().getFullYear();
		},
	},
});

app.engine("hbs", hbs.engine);
app.set("view engine", "hbs");
app.set("views", path.join(__dirname, "views"));

app.use(express.static(path.join(__dirname, "public")));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(
	session({
		secret: "a7x9k2m4p8q1w3e5",
		resave: false,
		saveUninitialized: true,
		cookie: { maxAge: 3600000 },
	})
);

// Gallery item data
const galleryItems = [
	{
		id: 1,
		name: "DSC02674_11",
		artist: "Unknown",
		description: "Computer Abstract Art Image",
		image: "r1.jpg",
		price: "8.50",
		category: "abstract",
	},
	{
		id: 2,
		name: "Urban Street-Art",
		artist: "Amsterdam Collective",
		description:
			"Graffiti on a wooden construction-wall on Plantage Muidergracht",
		image: "r2.jpg",
		price: "5.60",
		category: "street",
	},
	{
		id: 3,
		name: "Abstract-9974",
		artist: "Digital Studios",
		description: "Abstract Art Image",
		image: "r3.jpg",
		price: "6.50",
		category: "abstract",
	},
	{
		id: 4,
		name: "Art 235",
		artist: "Composite Lab",
		description: "Composite Image",
		image: "r4.jpg",
		price: "4.80",
		category: "digital",
	},
	{
		id: 5,
		name: "Radiographic Image",
		artist: "Indianapolis Museum",
		description:
			"African Songye Power Figure in the collection of the Indianapolis Museum of Art",
		image: "r5.jpg",
		price: "11.30",
		category: "photography",
	},
	{
		id: 6,
		name: "Abstract00BO",
		artist: "BTerryCompton",
		description: "BTerryCompton Abstract Art Image",
		image: "r6.jpg",
		price: "8.40",
		category: "abstract",
	},
	{
		id: 7,
		name: "Aliens Laughing",
		artist: "SciFi Arts",
		description: "Young gray aliens reading books, laughing",
		image: "r7.jpg",
		price: "6.50",
		category: "digital",
	},
	{
		id: 8,
		name: "Flower #56",
		artist: "Nature Collective",
		description: "134 flowers Sea Lavender Art",
		image: "r8.jpg",
		price: "9.00",
		category: "nature",
	},
	{
		id: 9,
		name: "White Wolves",
		artist: "CPM Art",
		description: "CPM Art Challenge Photo White Wolves, 2013",
		image: "r9.jpg",
		price: "7.30",
		category: "photography",
	},
];

// Simple user store
const users = {};

// Middleware for auth check
function requireAuth(req, res, next) {
	if (!req.session.user) {
		return res.redirect("/account/signin");
	}
	next();
}

// Homepage - gallery listing
app.get("/", function (req, res) {
	const category = req.query.category || "all";
	let items = galleryItems;
	if (category !== "all") {
		items = galleryItems.filter(function (item) {
			return item.category === category;
		});
	}
	res.render("home", {
		title: "Artisan Gallery",
		items: items,
		category: category,
		user: req.session.user || null,
		categories: ["all", "abstract", "street", "digital", "photography", "nature"],
	});
});

// Artwork detail page
app.get("/artwork/:id", function (req, res) {
	const item = galleryItems.find(function (g) {
		return g.id === parseInt(req.params.id, 10);
	});
	if (!item) {
		return res.status(404).render("error", {
			title: "Not Found",
			message: "Artwork not found",
		});
	}
	res.render("artwork", {
		title: item.name + " | Artisan Gallery",
		item: item,
		user: req.session.user || null,
	});
});

// Exhibition page with configurable display preferences
app.get("/exhibition/view", function (req, res) {
	const theme = req.query.theme || "modern";
	const exhibitionData = {
		title: "Current Exhibition | Artisan Gallery",
		exhibitionName: "Perspectives in Modern Art",
		curator: "Dr. Elena Vasquez",
		description:
			"A curated collection exploring the boundaries between traditional and digital art forms.",
		openingDate: "March 15, 2024",
		closingDate: "June 30, 2024",
		items: galleryItems.slice(0, 6),
		theme: theme,
		user: req.session.user || null,
	};
	res.render("exhibition", { ...exhibitionData, ...req.query });
});

// About page
app.get("/about", function (req, res) {
	res.render("about", {
		title: "About | Artisan Gallery",
		user: req.session.user || null,
	});
});

// Sign in
app.get("/account/signin", function (req, res) {
	res.render("signin", {
		title: "Sign In | Artisan Gallery",
		error: req.query.error || null,
	});
});

app.post("/account/signin", function (req, res) {
	const email = req.body.email;
	const password = req.body.password;
	if (!email || !password) {
		return res.redirect("/account/signin?error=Please+fill+in+all+fields");
	}
	const user = users[email];
	if (!user || user.password !== password) {
		return res.redirect("/account/signin?error=Invalid+credentials");
	}
	req.session.user = { email: user.email, name: user.name };
	res.redirect("/");
});

// Sign up
app.get("/account/signup", function (req, res) {
	res.render("signup", {
		title: "Sign Up | Artisan Gallery",
		error: req.query.error || null,
	});
});

app.post("/account/signup", function (req, res) {
	const name = req.body.name;
	const email = req.body.email;
	const password = req.body.password;
	if (!name || !email || !password) {
		return res.redirect("/account/signup?error=Please+fill+in+all+fields");
	}
	if (users[email]) {
		return res.redirect("/account/signup?error=Email+already+registered");
	}
	users[email] = { name: name, email: email, password: password };
	req.session.user = { email: email, name: name };
	res.redirect("/");
});

// Sign out
app.get("/account/signout", function (req, res) {
	req.session.destroy();
	res.redirect("/");
});

// Settings page
app.get("/account/settings", requireAuth, function (req, res) {
	res.render("settings", {
		title: "Settings | Artisan Gallery",
		user: req.session.user,
	});
});

// Health check
app.get("/healthz", function (req, res) {
	res.status(200).send("ok");
});

// 404 handler
app.use(function (req, res) {
	res.status(404).render("error", {
		title: "Not Found",
		message: "The page you are looking for does not exist.",
	});
});

// Error handler
app.use(function (err, req, res, next) {
	res.status(500).render("error", {
		title: "Error",
		message: "An internal error occurred.",
	}, function (renderErr, html) {
		if (renderErr) {
			res.status(500).type("text/plain").send("Internal Server Error");
		} else {
			res.send(html);
		}
	});
});

app.listen(PORT, function () {
	console.log("Artisan Gallery listening on port " + PORT);
});
