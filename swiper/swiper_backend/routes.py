import copy
import re
from swiper import app

from flask import request, render_template, jsonify, send_from_directory

# from database.db.models.labeling import LabelingSession, LabeledImage, Label
from database.db.models.user import TinderUser, Image

from database.db import Session


# @app.route("/api/lablingsession", methods=["POST"])
# def create_labling_session():
#     request_json = request.get_json()
#
#     session = Session()


# @app.route("/api/user", methods=["POST"])
# def get_next_image():
#     """
#
#     :return:
#     """
#     request_json = request.get_json()
#
#     if "labeling_session_id" not in request_json:
#         return jsonify({"error": "You must pass an id!"})
#
#     session = Session()
#
#     labeled_images = session.query(LabeledImage).filter(
#         LabeledImage.sessions == request_json["labeling_session_id"]).all()
#
#     labaled_image_ids = map(lambda x: x.id, labeled_images)
#
#     query = session.query(LabeledImage).filter(~LabeledImage.id.any(Image.id.in_(labaled_image_ids)))
#     image = query.first()
#     session.close()
#
#     return jsonify({"result": image.file_path})

#
# @app.route("/api/session", methods=["PUT"])
# def create_labeling_session():
#     request_json = request.get_json()
#
#     if "name" not in request_json:
#         return jsonify({"error": "You must pass a name"})
#
#     session = Session()
#     labeling_session = LabelingSession(name=request_json["name"])
#
#     session.add(labeling_session)
#     session.commit()
#     session.close()
#
#     return jsonify({"session_id": session.id})


@app.route("/api/search", methods=["GET"])
def search_users():
    search_query = request.args.get("query")

    if search_query is None:
        return jsonify({"error": "Please define a search query!"})

    session = Session()
    query = session.query(TinderUser).order_by(TinderUser.name) \
        .filter(TinderUser.name == search_query)
    users = query.all()
    response = {"data": [user.get_info() for user in users]}

    session.close()

    return jsonify(response)


def clean_arg(x):
    print(x)
    return re.sub("\"", "", x)


def clean_id(str_id: str) -> str:
    return str_id.replace("_", "-")


@app.route("/api/images", methods=["POST"])
def get_image():
    response_json = request.get_json()
    image_id = response_json.get("image_id")

    if image_id is None:
        return jsonify({"error": "Please pass an image id"})

    image_id = clean_id(image_id)

    session = Session()
    image = session.query(Image).filter_by(id=image_id).first()
    session.close()

    return send_from_directory(MEDIA_FOLDER, image.file_path, as_attachment=True)



@app.route("image")
def serve_image():
    render_template("")


@app.route("/api/profiles", methods=["GET"])
def get_profiles():
    page = request.args.get("page", default=0)
    page_size = request.args.get("page_size", default=10)

    if not isinstance(page, int):
        try:
            page = int(page)
        except Exception as e:
            pass
    if not isinstance(page_size, int):
        try:
            page_size = int(page_size)
        except Exception as e:
            pass

    session = Session()
    query = session.query(TinderUser).order_by(TinderUser.name).offset(page * page_size) \
        .limit(page_size)
    users = query.all()
    response = {"data": [user.get_info() for user in users]}

    session.close()

    return jsonify(response)


@app.route("/")
def viewer_home():
    return render_template("image_viewer.html")
