# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import validators, StringField, IntegerField, SelectField, PasswordField

from flask import flash
from application import ldap_mgr
from flask import current_app
import ldap

class AddUserForm(FlaskForm):
    name = StringField('Name', [validators.required(), validators.Length(min=2, max=16)])
    depart = StringField('Department', [validators.required(), validators.Length(min=4, max=64)])
    email = StringField('E-mail', [validators.required(), validators.Email()])

class LoginForm(FlaskForm):
    username = StringField('Name', [validators.required(), validators.length(min=2, max=20)])
    password = PasswordField('Password', [validators.required(), validators.length(min=6, max=64)])

    def validate_ldap(self):
        # 'Validate the username/password data against ldap directory'
        username = self.username.data
        password = self.password.data

        if not current_app.config['LDAP_ENABLED']:
            self.user = ldap_mgr._save_user(username, {'username': username, "password": password, 'name': username, 'email': username + '@test.com'})
            return True

        try:
            userdata = ldap_mgr.ldap_login(username, password)
        except ldap.INVALID_CREDENTIALS:
            flash("Invalid LDAP credentials", 'danger')
            # flash("Invalid LDAP credentials", 'danger')
            return False
        except ldap.LDAPError as err:
            if isinstance(err.message, dict):
                message = err.message.get('desc', str(err))
            else:
                message = str(err.message)
            flash(message, 'danger')
            return False

        if userdata is None:
            flash("Invalid LDAP credentials", 'danger')
            return False

        self.user = ldap_mgr._save_user(username, userdata)
        return True

    def validate(self, *args, **kwargs):
        """
        Validates the form by calling `validate` on each field, passing any
        extra `Form.validate_<fieldname>` validators to the field validator.

        also calls `validate_ldap`
        """

        valid = FlaskForm.validate(self, *args, **kwargs)
        if not valid:
            return valid

        return self.validate_ldap()