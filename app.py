from flask import Flask, render_template, request, redirect, url_for, session, flash

from models import db, Item, User, Claim, Notification, Message

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask_socketio import SocketIO, emit, join_room

import os

app = Flask(__name__)


# =====================================================
# APP CONFIGURATION
# =====================================================

app.config["SECRET_KEY"] = "smart-lost-found-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lost_found.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =====================================================
# SOCKET.IO
# =====================================================

socketio = SocketIO(app)


# =====================================================
# IMAGE UPLOAD CONFIGURATION
# =====================================================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# INITIALIZE DATABASE
# =====================================================

db.init_app(app)


# =====================================================
# INDIA TIMEZONE
# =====================================================

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


# =====================================================
# IST TEMPLATE FILTER
# =====================================================


@app.template_filter("ist")
def convert_to_ist(value):

    if not value:
        return ""

    if value.tzinfo is None:
        utc_time = value.replace(tzinfo=timezone.utc)
    else:
        utc_time = value.astimezone(timezone.utc)

    india_time = utc_time.astimezone(INDIA_TIMEZONE)

    return india_time.strftime("%d %b %Y, %I:%M %p")


# =====================================================
# NOTIFICATION COUNT
# =====================================================


@app.context_processor
def inject_notification_count():

    unread_count = 0

    if "user_id" in session:

        unread_count = Notification.query.filter_by(
            user_id=session["user_id"], is_read=False
        ).count()

    return {"unread_notification_count": unread_count}


# =====================================================
# LIVE NOTIFICATION COUNT FUNCTION
# =====================================================


def send_notification_count(user_id):
    """
    Database se latest unread notification count nikalta hai
    aur particular user ke browser ko Socket.IO ke through
    live update bhejta hai.
    """

    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    room = f"user_{user_id}"

    socketio.emit(
        "notification_count_update", {"unread_count": unread_count}, room=room
    )

    print(f"[NOTIFICATION] User {user_id} -> unread count: {unread_count}")


# =====================================================
# SOCKET.IO - USER CONNECT
# =====================================================


@socketio.on("connect")
def handle_connect():

    # -------------------------------------------------
    # LOGIN CHECK
    # -------------------------------------------------

    if "user_id" not in session:
        return

    user_id = session["user_id"]

    # -------------------------------------------------
    # PERSONAL USER ROOM
    # -------------------------------------------------

    room = f"user_{user_id}"

    join_room(room)

    print(f"[SOCKET] User {user_id} connected to room {room}")

    # -------------------------------------------------
    # SEND CURRENT NOTIFICATION COUNT
    # -------------------------------------------------

    send_notification_count(user_id)


# =====================================================
# LOGIN REQUIRED DECORATOR
# =====================================================


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash("Please login first to continue.", "error")

            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# =====================================================
# MATCHING FUNCTION
# =====================================================


def calculate_match_score(lost_item, found_item):

    score = 0

    # =================================================
    # CATEGORY - 40
    # =================================================

    if (
        lost_item.category
        and found_item.category
        and lost_item.category.lower() == found_item.category.lower()
    ):
        score += 40

    # =================================================
    # LOCATION - 30
    # =================================================

    if (
        lost_item.location
        and found_item.location
        and (
            lost_item.location.lower() in found_item.location.lower()
            or found_item.location.lower() in lost_item.location.lower()
        )
    ):
        score += 30

    # =================================================
    # NAME - 20
    # =================================================

    if (
        lost_item.name
        and found_item.name
        and (
            lost_item.name.lower() in found_item.name.lower()
            or found_item.name.lower() in lost_item.name.lower()
        )
    ):
        score += 20

    # =================================================
    # DESCRIPTION - 10
    # =================================================

    if lost_item.description and found_item.description:

        lost_words = set(lost_item.description.lower().split())

        found_words = set(found_item.description.lower().split())

        common_words = lost_words.intersection(found_words)

        if common_words:
            score += 10

    return score


# =====================================================
# HOME PAGE
# =====================================================


@app.route("/")
def home():

    recent_items = Item.query.order_by(Item.id.desc()).limit(6).all()

    return render_template("index.html", recent_items=recent_items)


# =====================================================
# SEARCH ITEMS
# =====================================================


@app.route("/search")
def search():

    keyword = request.args.get("q", "").strip()

    category = request.args.get("category", "").strip()

    item_type = request.args.get("type", "").strip()

    location = request.args.get("location", "").strip()

    query = Item.query

    # =================================================
    # KEYWORD SEARCH
    # =================================================

    if keyword:

        search_pattern = f"%{keyword}%"

        query = query.filter(
            db.or_(
                Item.name.ilike(search_pattern),
                Item.description.ilike(search_pattern),
                Item.location.ilike(search_pattern),
            )
        )

    # =================================================
    # CATEGORY FILTER
    # =================================================

    if category:

        query = query.filter(Item.category.ilike(category))

    # =================================================
    # LOST / FOUND FILTER
    # =================================================

    if item_type:

        query = query.filter(Item.item_type == item_type)

    # =================================================
    # LOCATION FILTER
    # =================================================

    if location:

        query = query.filter(Item.location.ilike(f"%{location}%"))

    results = query.order_by(Item.id.desc()).all()

    return render_template(
        "search.html",
        results=results,
        keyword=keyword,
        category=category,
        item_type=item_type,
        location=location,
    )


# =====================================================
# REGISTER
# =====================================================


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get("email", "").strip().lower()

        password = request.form.get("password", "")

        confirm_password = request.form.get("confirm_password", "")
        phone = request.form.get("phone", "").strip()

        # =================================================
        # VALIDATION
        # =================================================

        if not name or not email or not password:

            flash("Please fill in all fields.", "error")

            return redirect(url_for("register"))

        if password != confirm_password:

            flash("Passwords do not match.", "error")

            return redirect(url_for("register"))

        if len(password) < 6:

            flash("Password must contain at least 6 characters.", "error")

            return redirect(url_for("register"))

        # =================================================
        # CHECK EXISTING USER
        # =================================================

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            flash("An account with this email already exists.", "error")

            return redirect(url_for("register"))

        # =================================================
        # HASH PASSWORD
        # =================================================

        hashed_password = generate_password_hash(password)

        # =================================================
        # CREATE USER
        # =================================================

        new_user = User(name=name, email=email, password=hashed_password)

        db.session.add(new_user)

        db.session.commit()

        flash("Registration successful! Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# =====================================================
# LOGIN
# =====================================================


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email

            flash("Login successful!", "success")

            return redirect(url_for("home"))

        flash("Invalid email or password.", "error")

        return redirect(url_for("login"))

    return render_template("login.html")


# =====================================================
# LOGOUT
# =====================================================


@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("home"))


# =====================================================
# USER DASHBOARD
# =====================================================


@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]

    user = User.query.get_or_404(user_id)

    user_items = (
        Item.query
        .filter_by(user_id=user_id)
        .order_by(Item.id.desc())
        .all()
    )

    lost_reports = (
        Item.query
        .filter_by(user_id=user_id, item_type="Lost")
        .count()
    )

    found_reports = (
        Item.query
        .filter_by(user_id=user_id, item_type="Found")
        .count()
    )

    total_reports = lost_reports + found_reports

    pending_claims = (
        Claim.query
        .filter_by(claimant_id=user_id, status="Pending")
        .count()
    )

    approved_claims = (
        Claim.query
        .filter_by(claimant_id=user_id, status="Approved")
        .count()
    )

    recent_reports = (
        Item.query
        .filter_by(user_id=user_id)
        .order_by(Item.id.desc())
        .limit(5)
        .all()
    )

    recent_notifications = (
        Notification.query
        .filter_by(user_id=user_id)
        .order_by(Notification.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        user=user,
        total_reports=total_reports,
        lost_reports=lost_reports,
        found_reports=found_reports,
        pending_claims=pending_claims,
        approved_claims=approved_claims,
        recent_reports=recent_reports,
        recent_notifications=recent_notifications,
    )


# =====================================================
# USER PROFILE
# =====================================================


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    user_id = session["user_id"]

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get("email", "").strip().lower()

        phone = request.form.get("phone", "").strip()

        current_password = request.form.get("current_password", "")

        new_password = request.form.get("new_password", "")

        confirm_password = request.form.get("confirm_password", "")

        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not name or not email:

            flash("Name and email are required.", "error")

            return redirect(url_for("profile"))

        # =================================================
        # EMAIL DUPLICATE CHECK
        # =================================================

        existing_user = User.query.filter(
            User.email == email, User.id != user_id
        ).first()

        if existing_user:

            flash("This email is already registered with another account.", "error")

            return redirect(url_for("profile"))

        # =================================================
        # UPDATE NAME + EMAIL
        # =================================================

        user.name = name
        user.email = email
        user.phone = phone

        # =================================================
        # PASSWORD UPDATE
        # =================================================

        if new_password:

            if not current_password:

                flash("Enter your current password to change the password.", "error")

                return redirect(url_for("profile"))

            if not check_password_hash(user.password, current_password):

                flash("Current password is incorrect.", "error")

                return redirect(url_for("profile"))

            if len(new_password) < 6:

                flash("New password must contain at least 6 characters.", "error")

                return redirect(url_for("profile"))

            if new_password != confirm_password:

                flash("New passwords do not match.", "error")

                return redirect(url_for("profile"))

            user.password = generate_password_hash(new_password)

        # =================================================
        # SAVE CHANGES
        # =================================================

        db.session.commit()

        # =================================================
        # UPDATE SESSION
        # =================================================

        session["user_name"] = user.name
        session["user_email"] = user.email

        flash("Profile updated successfully!", "success")

        return redirect(url_for("profile"))

    # =================================================
    # PROFILE STATISTICS
    # =================================================

    total_reports = Item.query.filter_by(user_id=user_id).count()

    lost_count = Item.query.filter_by(user_id=user_id, item_type="Lost").count()

    found_count = Item.query.filter_by(user_id=user_id, item_type="Found").count()

    claims_count = Claim.query.filter_by(claimant_id=user_id).count()

    return render_template(
        "profile.html",
        user=user,
        total_reports=total_reports,
        lost_count=lost_count,
        found_count=found_count,
        claims_count=claims_count,
    )


# =====================================================
# REPORT LOST ITEM
# =====================================================


@app.route("/lost", methods=["GET", "POST"])
@login_required
def report_lost():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        category = request.form.get("category", "").strip()

        description = request.form.get("description", "").strip()

        location = request.form.get("location", "").strip()

        date = request.form.get("date", "").strip()

        contact = request.form.get("contact", "").strip()

        # =================================================
        # OTHER CATEGORY
        # =================================================

        if category.lower() == "other":

            other_category = request.form.get("other_category", "").strip()

            if other_category:
                category = other_category

        # =================================================
        # IMAGE
        # =================================================

        image_file = request.files.get("image")

        image_filename = None

        if image_file and image_file.filename:

            image_filename = secure_filename(image_file.filename)

            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        # =================================================
        # CREATE LOST ITEM
        # =================================================

        new_item = Item(
            name=name,
            category=category,
            description=description,
            location=location,
            date=date,
            item_type="Lost",
            contact=contact,
            image=image_filename,
            user_id=session["user_id"],
        )

        db.session.add(new_item)

        db.session.commit()

        flash("Lost item reported successfully!", "success")

        return redirect(url_for("home"))

    return render_template("lost.html")


# =====================================================
# REPORT FOUND ITEM
# =====================================================


@app.route("/found", methods=["GET", "POST"])
@login_required
def report_found():

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        category = request.form.get("category", "").strip()

        description = request.form.get("description", "").strip()

        location = request.form.get("location", "").strip()

        date = request.form.get("date", "").strip()

        contact = request.form.get("contact", "").strip()

        # =================================================
        # OTHER CATEGORY
        # =================================================

        if category.lower() == "other":

            other_category = request.form.get("other_category", "").strip()

            if other_category:
                category = other_category

        # =================================================
        # IMAGE
        # =================================================

        image_file = request.files.get("image")

        image_filename = None

        if image_file and image_file.filename:

            image_filename = secure_filename(image_file.filename)

            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        # =================================================
        # CREATE FOUND ITEM
        # =================================================

        new_item = Item(
            name=name,
            category=category,
            description=description,
            location=location,
            date=date,
            item_type="Found",
            contact=contact,
            image=image_filename,
            user_id=session["user_id"],
        )

        db.session.add(new_item)

        db.session.flush()

        # =================================================
        # AUTOMATIC SMART MATCHING
        # =================================================

        lost_items = Item.query.filter_by(item_type="Lost").all()

        match_notifications = 0

        # -------------------------------------------------
        # USERS WHO NEED LIVE COUNT UPDATE
        # -------------------------------------------------

        notified_users = set()

        for lost_item in lost_items:

            # =================================================
            # USER SHOULD NOT GET SELF-MATCH
            # =================================================

            if lost_item.user_id == session["user_id"]:
                continue

            # =================================================
            # CALCULATE SCORE
            # =================================================

            score = calculate_match_score(lost_item, new_item)

            # =================================================
            # POSSIBLE MATCH
            # =================================================

            if score >= 40:

                # =================================================
                # DUPLICATE NOTIFICATION PROTECTION
                # =================================================

                existing_notification = (
                    Notification.query.filter_by(
                        user_id=lost_item.user_id, type="match"
                    )
                    .filter(Notification.message.ilike(f"%'{new_item.name}'%"))
                    .first()
                )

                if existing_notification:
                    continue

                # =================================================
                # CREATE MATCH NOTIFICATION
                # =================================================

                notification = Notification(
                    user_id=lost_item.user_id,
                    claim_id=None,
                    type="match",
                    is_read=False,
                    message=(
                        f"Possible match found! "
                        f"A found item named "
                        f"'{new_item.name}' "
                        f"matches your lost item "
                        f"'{lost_item.name}' "
                        f"with a {score}% match score."
                    ),
                )

                db.session.add(notification)

                # -------------------------------------------------
                # ADD USER FOR LIVE UPDATE
                # -------------------------------------------------

                notified_users.add(lost_item.user_id)

                match_notifications += 1

        # =================================================
        # SAVE FOUND ITEM + NOTIFICATIONS
        # =================================================

        db.session.commit()

        # =================================================
        # LIVE NOTIFICATION COUNT UPDATE
        # =================================================

        for user_id in notified_users:

            send_notification_count(user_id)

        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        if match_notifications > 0:

            flash(
                "Found item reported successfully! "
                "Possible matches have been notified.",
                "success",
            )

        else:

            flash("Found item reported successfully!", "success")

        return redirect(url_for("home"))

    return render_template("found.html")


# =====================================================
# MY REPORTS
# =====================================================


@app.route("/my-reports")
@login_required
def my_reports():

    user_id = session["user_id"]

    # =================================================
    # USER ITEMS
    # =================================================

    my_items = Item.query.filter_by(user_id=user_id).order_by(Item.id.desc()).all()

    # =================================================
    # APPROVED CLAIMS
    # =================================================

    approved_claims = {}

    for item in my_items:

        if item.item_type == "Lost":

            claim = (
                Claim.query.filter_by(
                    claimant_id=user_id, lost_item_id=item.id, status="Approved"
                )
                .order_by(Claim.id.desc())
                .first()
            )

            if claim:

                approved_claims[item.id] = claim

    return render_template(
        "my_reports.html", my_items=my_items, approved_claims=approved_claims
    )


# =====================================================
# CLAIM ITEM
# =====================================================


@app.route("/claim/<int:item_id>", methods=["GET", "POST"])
@login_required
def claim_item(item_id):

    found_item = Item.query.get_or_404(item_id)

    # =================================================
    # ONLY FOUND ITEMS
    # =================================================

    if found_item.item_type != "Found":

        flash("Only found items can be claimed.", "error")

        return redirect(url_for("search"))

    # =================================================
    # USER CANNOT CLAIM OWN ITEM
    # =================================================

    if found_item.user_id == session["user_id"]:

        flash("You cannot claim an item that you reported yourself.", "error")

        return redirect(url_for("search"))

    # =================================================
    # USER'S LOST ITEMS
    # =================================================

    lost_items = (
        Item.query.filter_by(user_id=session["user_id"], item_type="Lost")
        .order_by(Item.id.desc())
        .all()
    )

    # =================================================
    # SUBMIT CLAIM
    # =================================================

    if request.method == "POST":

        lost_item_id = request.form.get("lost_item_id")

        message = request.form.get("message", "").strip()

        # =================================================
        # FIND LOST ITEM
        # =================================================

        lost_item = Item.query.filter_by(
            id=lost_item_id, user_id=session["user_id"], item_type="Lost"
        ).first()

        if not lost_item:

            flash("Invalid lost item selected.", "error")

            return redirect(url_for("claim_item", item_id=item_id))

        # =================================================
        # CHECK DUPLICATE CLAIM
        # =================================================

        existing_claim = Claim.query.filter_by(
            claimant_id=session["user_id"],
            lost_item_id=lost_item.id,
            found_item_id=found_item.id,
        ).first()

        if existing_claim:

            flash("You have already submitted a claim for this item.", "error")

            return redirect(url_for("my_reports"))

        # =================================================
        # CREATE CLAIM
        # =================================================

        new_claim = Claim(
            claimant_id=session["user_id"],
            lost_item_id=lost_item.id,
            found_item_id=found_item.id,
            message=message,
            status="Pending",
        )

        db.session.add(new_claim)

        db.session.flush()

        # =================================================
        # NOTIFY FOUND ITEM OWNER
        # =================================================

        notification = Notification(
            user_id=found_item.user_id,
            claim_id=new_claim.id,
            message=(
                f"{session['user_name']} has submitted "
                f"a claim for your found item "
                f"'{found_item.name}'."
            ),
            type="claim",
            is_read=False,
        )

        db.session.add(notification)

        db.session.commit()

        # =================================================
        # LIVE NOTIFICATION COUNT
        # =================================================

        send_notification_count(found_item.user_id)

        flash("Claim submitted successfully!", "success")

        return redirect(url_for("my_reports"))

    return render_template("claim.html", found_item=found_item, lost_items=lost_items)


# =====================================================
# SMART MATCHING PAGE
# =====================================================


@app.route("/matches/<int:item_id>")
@login_required
def matches(item_id):

    lost_item = Item.query.get_or_404(item_id)

    # =================================================
    # SECURITY
    # =================================================

    if lost_item.user_id != session["user_id"]:

        flash("You can only view matches for your own lost items.", "error")

        return redirect(url_for("my_reports"))

    # =================================================
    # ONLY LOST ITEMS
    # =================================================

    if lost_item.item_type != "Lost":

        flash("Matching is available for lost items only.", "error")

        return redirect(url_for("my_reports"))

    # =================================================
    # FIND FOUND ITEMS
    # =================================================

    found_items = Item.query.filter_by(item_type="Found").all()

    matches = []

    # =================================================
    # MATCHING ALGORITHM
    # =================================================

    for found_item in found_items:

        score = calculate_match_score(lost_item, found_item)

        if score >= 40:

            matches.append({"item": found_item, "score": score})

    # =================================================
    # SORT
    # =================================================

    matches.sort(key=lambda x: x["score"], reverse=True)

    return render_template("matches.html", lost_item=lost_item, matches=matches)


# =====================================================
# VIEW CLAIMS FOR MY FOUND ITEM
# =====================================================


@app.route("/claims/<int:item_id>")
@login_required
def view_claims(item_id):

    item = Item.query.get_or_404(item_id)

    # =================================================
    # ONLY ITEM OWNER
    # =================================================

    if item.user_id != session["user_id"]:

        flash("You are not allowed to view these claims.", "error")

        return redirect(url_for("my_reports"))

    # =================================================
    # ONLY FOUND ITEMS
    # =================================================

    if item.item_type != "Found":

        flash("Claims are available for found items only.", "error")

        return redirect(url_for("my_reports"))

    claims = (
        Claim.query.filter_by(found_item_id=item.id).order_by(Claim.id.desc()).all()
    )

    return render_template("claims.html", item=item, claims=claims)


# =====================================================
# VIEW CLAIM FROM NOTIFICATION
# =====================================================


@app.route("/notification/<int:notification_id>/claim")
@login_required
def notification_claim(notification_id):

    notification = Notification.query.get_or_404(notification_id)

    # =================================================
    # SECURITY
    # =================================================

    if notification.user_id != session["user_id"]:

        flash("You are not allowed to access this notification.", "error")

        return redirect(url_for("notifications"))

    # =================================================
    # NO CLAIM
    # =================================================

    if not notification.claim_id:

        flash("This notification has no claim attached.", "error")

        return redirect(url_for("notifications"))

    claim = Claim.query.get_or_404(notification.claim_id)

    found_item = Item.query.get_or_404(claim.found_item_id)

    # =================================================
    # MARK READ
    # =================================================

    notification.is_read = True

    db.session.commit()

    # =================================================
    # LIVE COUNT UPDATE
    # =================================================

    send_notification_count(session["user_id"])

    return redirect(url_for("view_claims", item_id=found_item.id))


# =====================================================
# VIEW MATCH FROM NOTIFICATION
# =====================================================


@app.route("/notification/<int:notification_id>/match")
@login_required
def notification_match(notification_id):

    notification = Notification.query.get_or_404(notification_id)

    # =================================================
    # SECURITY
    # =================================================

    if notification.user_id != session["user_id"]:

        flash("You are not allowed to access this notification.", "error")

        return redirect(url_for("notifications"))

    # =================================================
    # ONLY MATCH NOTIFICATION
    # =================================================

    if notification.type != "match":

        flash("Invalid match notification.", "error")

        return redirect(url_for("notifications"))

    # =================================================
    # MARK READ
    # =================================================

    notification.is_read = True

    db.session.commit()

    # =================================================
    # LIVE COUNT UPDATE
    # =================================================

    send_notification_count(session["user_id"])

    # =================================================
    # OPEN MY REPORTS
    # =================================================

    return redirect(url_for("my_reports"))


# =====================================================
# APPROVE / REJECT CLAIM
# =====================================================


@app.route("/claim/<int:claim_id>/<action>", methods=["POST"])
@login_required
def update_claim_status(claim_id, action):

    claim = Claim.query.get_or_404(claim_id)

    found_item = Item.query.get_or_404(claim.found_item_id)

    # =================================================
    # SECURITY
    # =================================================

    if found_item.user_id != session["user_id"]:

        flash("You are not allowed to update this claim.", "error")

        return redirect(url_for("my_reports"))

    # =================================================
    # MUST BE PENDING
    # =================================================

    if claim.status != "Pending":

        flash(f"This claim has already been " f"{claim.status.lower()}.", "error")

        return redirect(url_for("view_claims", item_id=found_item.id))

    # =================================================
    # APPROVE
    # =================================================

    if action == "approve":

        claim.status = "Approved"

        notification = Notification(
            user_id=claim.claimant_id,
            claim_id=claim.id,
            message=(
                f"Your claim for "
                f"'{found_item.name}' has been approved. "
                f"You can now contact the person who "
                f"found your item."
            ),
            type="claim_approved",
            is_read=False,
        )

        db.session.add(notification)

        flash("Claim approved successfully.", "success")

        # -------------------------------------------------
        # STORE RECEIVER ID FOR LIVE COUNT
        # -------------------------------------------------

        notification_receiver_id = claim.claimant_id

    # =================================================
    # REJECT
    # =================================================

    elif action == "reject":

        claim.status = "Rejected"

        notification = Notification(
            user_id=claim.claimant_id,
            claim_id=claim.id,
            message=(
                f"Your claim for "
                f"'{found_item.name}' has been rejected "
                f"by the found item owner."
            ),
            type="claim_rejected",
            is_read=False,
        )

        db.session.add(notification)

        flash("Claim rejected successfully.", "success")

        # -------------------------------------------------
        # STORE RECEIVER ID FOR LIVE COUNT
        # -------------------------------------------------

        notification_receiver_id = claim.claimant_id

    else:

        flash("Invalid claim action.", "error")

        return redirect(url_for("view_claims", item_id=found_item.id))

    # =================================================
    # SAVE
    # =================================================

    db.session.commit()

    # =================================================
    # LIVE NOTIFICATION COUNT
    # =================================================

    send_notification_count(notification_receiver_id)

    return redirect(url_for("view_claims", item_id=found_item.id))


# =====================================================
# CONTACT FOUND PERSON
# =====================================================


@app.route("/contact-found/<int:claim_id>")
@login_required
def contact_found_person(claim_id):

    claim = Claim.query.get_or_404(claim_id)

    # =================================================
    # SECURITY
    # =================================================

    if claim.claimant_id != session["user_id"]:

        flash("You are not allowed to access this contact information.", "error")

        return redirect(url_for("my_reports"))

    # =================================================
    # ONLY APPROVED CLAIM
    # =================================================

    if claim.status != "Approved":

        flash("Contact information is available only after claim approval.", "error")

        return redirect(url_for("my_reports"))

    found_item = Item.query.get_or_404(claim.found_item_id)

    found_user = User.query.get_or_404(found_item.user_id)

    return render_template(
        "contact_found.html", claim=claim, found_item=found_item, found_user=found_user
    )


# =====================================================
# IN-APP MESSAGING
# =====================================================


@app.route("/messages/<int:claim_id>", methods=["GET", "POST"])
@login_required
def messages(claim_id):

    # =================================================
    # FIND CLAIM
    # =================================================

    claim = Claim.query.get_or_404(claim_id)

    # =================================================
    # ONLY APPROVED CLAIM
    # =================================================

    if claim.status != "Approved":

        flash("Messaging is available only after claim approval.", "error")

        return redirect(url_for("my_reports"))

    # =================================================
    # FIND ITEMS
    # =================================================

    lost_item = Item.query.get_or_404(claim.lost_item_id)

    found_item = Item.query.get_or_404(claim.found_item_id)

    # =================================================
    # SECURITY
    # =================================================

    is_claimant = session["user_id"] == claim.claimant_id

    is_found_owner = session["user_id"] == found_item.user_id

    if not is_claimant and not is_found_owner:

        flash("You are not allowed to access this conversation.", "error")

        return redirect(url_for("my_reports"))

    # =================================================
    # FIND OTHER USER
    # =================================================

    if is_claimant:

        other_user = User.query.get_or_404(found_item.user_id)

    else:

        other_user = User.query.get_or_404(claim.claimant_id)

    # =================================================
    # NORMAL MESSAGE SEND
    # =================================================

    if request.method == "POST":

        message_text = request.form.get("message", "").strip()

        if not message_text:

            flash("Message cannot be empty.", "error")

            return redirect(url_for("messages", claim_id=claim_id))

        if len(message_text) > 1000:

            flash("Message cannot exceed 1000 characters.", "error")

            return redirect(url_for("messages", claim_id=claim_id))

        # =================================================
        # CREATE MESSAGE
        # =================================================

        new_message = Message(
            sender_id=session["user_id"],
            receiver_id=other_user.id,
            claim_id=claim.id,
            message=message_text,
            is_read=False,
        )

        db.session.add(new_message)

        # =================================================
        # NOTIFICATION PREVIEW
        # =================================================

        notification_preview = message_text

        if len(notification_preview) > 150:

            notification_preview = notification_preview[:150] + "..."

        # =================================================
        # CREATE NOTIFICATION
        # =================================================

        notification = Notification(
            user_id=other_user.id,
            claim_id=claim.id,
            message=(
                f"{session['user_name']} sent you "
                f"a message about "
                f"'{found_item.name}': "
                f'"{notification_preview}"'
            ),
            type="message",
            is_read=False,
        )

        db.session.add(notification)

        db.session.commit()

        # =================================================
        # LIVE NOTIFICATION COUNT
        # =================================================

        send_notification_count(other_user.id)

        flash("Message sent successfully!", "success")

        return redirect(url_for("messages", claim_id=claim_id))

    # =================================================
    # GET CONVERSATION
    # =================================================

    conversation = (
        Message.query.filter_by(claim_id=claim.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    # =================================================
    # MARK RECEIVED MESSAGES AS READ
    # =================================================

    unread_messages = Message.query.filter_by(
        claim_id=claim.id, receiver_id=session["user_id"], is_read=False
    ).all()

    for message in unread_messages:

        message.is_read = True

    db.session.commit()

    return render_template(
        "messages.html",
        claim=claim,
        lost_item=lost_item,
        found_item=found_item,
        other_user=other_user,
        conversation=conversation,
    )


# =====================================================
# LIVE CHAT - JOIN ROOM
# =====================================================


@socketio.on("join_chat")
def handle_join_chat(data):

    # =================================================
    # LOGIN CHECK
    # =================================================

    if "user_id" not in session:
        return

    claim_id = data.get("claim_id")

    if not claim_id:
        return

    # =================================================
    # FIND CLAIM
    # =================================================

    claim = Claim.query.get(claim_id)

    if not claim:
        return

    # =================================================
    # ONLY APPROVED CLAIM
    # =================================================

    if claim.status != "Approved":
        return

    found_item = Item.query.get(claim.found_item_id)

    if not found_item:
        return

    # =================================================
    # SECURITY
    # =================================================

    current_user_id = session["user_id"]

    is_claimant = current_user_id == claim.claimant_id

    is_found_owner = current_user_id == found_item.user_id

    if not is_claimant and not is_found_owner:
        return

    # =================================================
    # JOIN CHAT ROOM
    # =================================================

    room = f"claim_{claim_id}"

    join_room(room)

    emit("chat_joined", {"message": "Connected to live chat."})


# =====================================================
# LIVE CHAT - SEND MESSAGE
# =====================================================


@socketio.on("send_message")
def handle_send_message(data):

    # =================================================
    # LOGIN CHECK
    # =================================================

    if "user_id" not in session:
        return

    claim_id = data.get("claim_id")

    message_text = data.get("message", "").strip()

    if not claim_id or not message_text:
        return

    # =================================================
    # MESSAGE LENGTH
    # =================================================

    if len(message_text) > 1000:

        emit("chat_error", {"message": "Message cannot exceed 1000 characters."})

        return

    # =================================================
    # FIND CLAIM
    # =================================================

    claim = Claim.query.get(claim_id)

    if not claim:
        return

    # =================================================
    # ONLY APPROVED CLAIM
    # =================================================

    if claim.status != "Approved":
        return

    # =================================================
    # FIND ITEMS
    # =================================================

    lost_item = Item.query.get(claim.lost_item_id)

    found_item = Item.query.get(claim.found_item_id)

    if not lost_item or not found_item:
        return

    # =================================================
    # CURRENT USER
    # =================================================

    current_user_id = session["user_id"]

    # =================================================
    # SECURITY
    # =================================================

    is_claimant = current_user_id == claim.claimant_id

    is_found_owner = current_user_id == found_item.user_id

    if not is_claimant and not is_found_owner:
        return

    # =================================================
    # FIND RECEIVER
    # =================================================

    if is_claimant:

        receiver_id = found_item.user_id

    else:

        receiver_id = claim.claimant_id

    # =================================================
    # SAVE MESSAGE
    # =================================================

    new_message = Message(
        sender_id=current_user_id,
        receiver_id=receiver_id,
        claim_id=claim.id,
        message=message_text,
        is_read=False,
    )

    db.session.add(new_message)

    # =================================================
    # NOTIFICATION PREVIEW
    # =================================================

    notification_preview = message_text

    if len(notification_preview) > 150:

        notification_preview = notification_preview[:150] + "..."

    # =================================================
    # CREATE NOTIFICATION
    # =================================================

    notification = Notification(
        user_id=receiver_id,
        claim_id=claim.id,
        message=(
            f"{session['user_name']} sent you "
            f"a message about "
            f"'{found_item.name}': "
            f'"{notification_preview}"'
        ),
        type="message",
        is_read=False,
    )

    db.session.add(notification)

    # =================================================
    # ONE DATABASE COMMIT
    # =================================================

    db.session.commit()

    # =================================================
    # LIVE NOTIFICATION COUNT
    # =================================================

    send_notification_count(receiver_id)

    # =================================================
    # FORMAT TIMESTAMP
    # =================================================

    message_time = new_message.created_at

    if message_time.tzinfo is None:

        message_time = message_time.replace(tzinfo=timezone.utc)

    message_time = message_time.astimezone(INDIA_TIMEZONE)

    formatted_time = message_time.strftime("%d %b %Y, %I:%M %p")

    # =================================================
    # SEND MESSAGE LIVE
    # =================================================

    room = f"claim_{claim.id}"

    emit(
        "new_message",
        {
            "id": new_message.id,
            "sender_id": current_user_id,
            "sender_name": session["user_name"],
            "message": new_message.message,
            "created_at": formatted_time,
        },
        room=room,
    )


# =====================================================
# LIVE CHAT - TYPING START
# =====================================================


@socketio.on("typing")
def handle_typing(data):

    if "user_id" not in session:
        return

    claim_id = data.get("claim_id")

    if not claim_id:
        return

    claim = Claim.query.get(claim_id)

    if not claim:
        return

    if claim.status != "Approved":
        return

    found_item = Item.query.get(claim.found_item_id)

    if not found_item:
        return

    current_user_id = session["user_id"]

    # =================================================
    # SECURITY
    # =================================================

    if current_user_id != claim.claimant_id and current_user_id != found_item.user_id:
        return

    room = f"claim_{claim.id}"

    emit(
        "user_typing",
        {"user_id": current_user_id, "user_name": session["user_name"]},
        room=room,
        include_self=False,
    )


# =====================================================
# LIVE CHAT - TYPING STOP
# =====================================================


@socketio.on("stop_typing")
def handle_stop_typing(data):

    if "user_id" not in session:
        return

    claim_id = data.get("claim_id")

    if not claim_id:
        return

    claim = Claim.query.get(claim_id)

    if not claim:
        return

    found_item = Item.query.get(claim.found_item_id)

    if not found_item:
        return

    current_user_id = session["user_id"]

    # =================================================
    # SECURITY
    # =================================================

    if current_user_id != claim.claimant_id and current_user_id != found_item.user_id:
        return

    room = f"claim_{claim.id}"

    emit(
        "user_stopped_typing",
        {"user_id": current_user_id},
        room=room,
        include_self=False,
    )


# =====================================================
# LIVE CHAT - USER ONLINE
# =====================================================


@socketio.on("chat_online")
def handle_chat_online(data):

    if "user_id" not in session:
        return

    claim_id = data.get("claim_id")

    if not claim_id:
        return

    claim = Claim.query.get(claim_id)

    if not claim:
        return

    if claim.status != "Approved":
        return

    found_item = Item.query.get(claim.found_item_id)

    if not found_item:
        return

    current_user_id = session["user_id"]

    if current_user_id != claim.claimant_id and current_user_id != found_item.user_id:
        return

    room = f"claim_{claim.id}"

    join_room(room)

    emit(
        "user_online",
        {"user_id": current_user_id, "user_name": session["user_name"]},
        room=room,
        include_self=False,
    )


# =====================================================
# OPEN MESSAGE FROM NOTIFICATION
# =====================================================


@app.route("/notifications/<int:notification_id>/message")
@login_required
def notification_message(notification_id):

    notification = Notification.query.get_or_404(notification_id)

    # =================================================
    # SECURITY
    # =================================================

    if notification.user_id != session["user_id"]:

        flash("You are not allowed to access this notification.", "error")

        return redirect(url_for("notifications"))

    # =================================================
    # CHECK CLAIM
    # =================================================

    if not notification.claim_id:

        flash("This notification has no conversation attached.", "error")

        return redirect(url_for("notifications"))

    claim = Claim.query.get_or_404(notification.claim_id)

    # =================================================
    # ONLY APPROVED CLAIM
    # =================================================

    if claim.status != "Approved":

        flash("Messaging is available only after claim approval.", "error")

        return redirect(url_for("notifications"))

    # =================================================
    # MARK READ
    # =================================================

    notification.is_read = True

    db.session.commit()

    # =================================================
    # LIVE COUNT UPDATE
    # =================================================

    send_notification_count(session["user_id"])

    return redirect(url_for("messages", claim_id=claim.id))


# =====================================================
# NOTIFICATIONS
# =====================================================


@app.route("/notifications")
@login_required
def notifications():

    user_notifications = (
        Notification.query.filter_by(user_id=session["user_id"])
        .order_by(Notification.id.desc())
        .all()
    )

    return render_template("notifications.html", notifications=user_notifications)


# =====================================================
# MARK ONE NOTIFICATION AS READ
# =====================================================


@app.route("/notifications/read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):

    notification = Notification.query.get_or_404(notification_id)

    # =================================================
    # SECURITY
    # =================================================

    if notification.user_id != session["user_id"]:

        flash("You are not allowed to access this notification.", "error")

        return redirect(url_for("notifications"))

    notification.is_read = True

    db.session.commit()

    # =================================================
    # LIVE COUNT UPDATE
    # =================================================

    send_notification_count(session["user_id"])

    return redirect(url_for("notifications"))


# =====================================================
# MARK ALL NOTIFICATIONS AS READ
# =====================================================


@app.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read():

    (
        Notification.query.filter_by(user_id=session["user_id"], is_read=False).update(
            {Notification.is_read: True}
        )
    )

    db.session.commit()

    # =================================================
    # LIVE COUNT UPDATE
    # =================================================

    send_notification_count(session["user_id"])

    flash("All notifications marked as read.", "success")

    return redirect(url_for("notifications"))


# =====================================================
# CREATE DATABASE TABLES
# =====================================================

with app.app_context():

    db.create_all()


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    socketio.run(app, debug=True)
