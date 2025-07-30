# config setting for file upload

UPLOAD_CONFIG = {
    "resume": {
        "subfolder": "resumes",
        "allowed_exts": {"pdf"},
        "max_size": 5 * 1024 * 1024,  # 5 MB
        "prefix": "resume"
    },
    "profile_image": {
        "subfolder": "profile_images",
        "allowed_exts": {"jpg", "jpeg", "png"},
        "max_size": 1 * 1024 * 1024,  # 1 MB
        "prefix": "image"
    },
    "logo": {
        "subfolder": "logos",
        "allowed_exts": {"jpg", "jpeg", "png"},
        "max_size": 1 * 1024 * 1024,  # 1 MB
        "prefix": "logo"
    }
}

# settings for profile info update
PROFILE_UPDATE_FIELDS = {
    "student": {
        "user_table": ["full_name"],
        "student_table": ["university", "course"],
        "can_edit_email": False
    },
    "employer": {
        "user_table": ["full_name"],
        "employer_table": ["company_name", "company_description", "website", "logo_path"],
        "can_edit_email": False
    },
    "admin": {
        "user_table": ["full_name", "email"],
        "can_edit_email": True
    }
}