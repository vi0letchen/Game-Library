from wtforms import Form, IntegerField, TextAreaField, SubmitField, validators

class ReviewForm(Form):
    rating = IntegerField('Rating (0-5)', [validators.NumberRange(min=0, max=5)])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Review')


