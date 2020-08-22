"""The forms for spatialMOS"""

from django import forms


class addressForm(forms.Form):
    """The form for address inputs"""
    COUNTRY_CHOICES = (('Austria', 'Österreich'), ('Italy', 'Italien'))

    street = forms.CharField(label='Straße', required=False)
    housenumber = forms.IntegerField(label='Hausnummer', required=False)
    postcode = forms.IntegerField(label='PLZ', required=False)
    city = forms.CharField(label='Ort', required=True)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False)

    street.widget.attrs.update({'placeholder': 'Straße'})
    housenumber.widget.attrs.update({'placeholder': 'Hausnummer'})
    city.widget.attrs.update({'placeholder': 'Ort'})
    postcode.widget.attrs.update({'placeholder': 'PLZ'})


class latlonForm(forms.Form):
    """The form for coordinates inputs"""
    latitude = forms.FloatField(label='Latitude', required=True, min_value=46, max_value=48)
    longitude = forms.FloatField(label='Longitude', required=True, min_value=9, max_value=12)

    latitude.widget.attrs.update({'placeholder': 'Latitude'})
    longitude.widget.attrs.update({'placeholder': 'Longitude'})