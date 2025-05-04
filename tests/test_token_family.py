from importlib import reload
from uuid import uuid4
from freezegun import freeze_time
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import (
    RefreshToken,
    AccessToken,
    FamilyMixin,
)
from rest_framework_simplejwt.token_family.models import TokenFamily, BlacklistedTokenFamily
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.utils import aware_utcnow

from .utils import override_api_settings


class TestTokenFamilyModels(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="test_user", password="test_password")

    def test_manual_family_creation(self):
        token_fam = TokenFamily.objects.create(
            user= self.user,
            family_id= uuid4().hex,
            created_at= aware_utcnow(),
            expires_at= aware_utcnow() + timedelta(days=1),
        )

        self.assertEqual(self.user.id, token_fam.user.id)

    def test_expires_at_is_none(self):
        token_fam = TokenFamily.objects.create(
            user= self.user,
            family_id= uuid4().hex,
            created_at= aware_utcnow(),
            expires_at= None,
        )

        self.assertIsNone(token_fam.expires_at)

    def test_expires_at_is_datetime(self):
        fam_id = uuid4().hex
        current_time = aware_utcnow()
        expiration_date = current_time + timedelta(days=1)
        token_fam = TokenFamily.objects.create(
            user= self.user,
            family_id= fam_id,
            created_at= current_time,
            expires_at= expiration_date,
        )

        self.assertEqual(token_fam.expires_at, expiration_date)

    def test_family_id_cannot_be_null(self):
        """
        If the code inside the 'with' block raises ValueError or IntegrityError, the test passes.
        If it does NOT raise one of these exceptions, the test fails.
        """
        with self.assertRaises((ValueError, IntegrityError)): # Catch either potential exception
            TokenFamily.objects.create(
                user= self.user,
                family_id= None,  # Intentionally try to set it to None
                created_at= aware_utcnow(),
                expires_at= aware_utcnow() + timedelta(days=1),
            )
    
    def test_created_at_cannot_be_null(self):
        """
        If the code inside the 'with' block raises ValueError or IntegrityError, the test passes.
        If it does NOT raise one of these exceptions, the test fails.
        """
        with self.assertRaises((ValueError, IntegrityError)): # Catch either potential exception
            TokenFamily.objects.create(
                user= self.user,
                family_id= uuid4().hex,
                created_at= None,
                expires_at= aware_utcnow() + timedelta(days=1),
            )

    def test_family_id_must_be_unique(self):
        fam_id = uuid4().hex
        TokenFamily.objects.create(
            user= self.user,
            family_id= fam_id,
            created_at= aware_utcnow(),
            expires_at= aware_utcnow() + timedelta(days=1),
        )

        with self.assertRaises((ValueError, IntegrityError)): # Catch either potential exception
            TokenFamily.objects.create(
                user= self.user,
                family_id= fam_id,
                created_at= aware_utcnow(),
                expires_at= aware_utcnow() + timedelta(days=1),
            )

    def test_user_can_have_multiple_families(self):
        num_families_to_create = 3 

        # loop to create multiple TokenFamily instances for the same user
        for i in range(num_families_to_create):
            TokenFamily.objects.create(
                user= self.user, 
                family_id= uuid4().hex,
                created_at= aware_utcnow(),
                expires_at= aware_utcnow() + timedelta(days=(i + 1)), 
            )

        self.assertEqual(TokenFamily.objects.filter(user=self.user).count(), num_families_to_create)

    def test_add_family_to_blacklist(self):
        token_fam = TokenFamily.objects.create(
            user= self.user, 
            family_id= uuid4().hex,
            created_at= aware_utcnow(),
            expires_at= aware_utcnow() + timedelta(days=1), 
        )

        blacklisted_fam = BlacklistedTokenFamily.objects.create(family= token_fam)

        self.assertEqual(BlacklistedTokenFamily.objects.all().count(), 1)
        self.assertEqual(token_fam.id, blacklisted_fam.family.id)

    def test_duplicate_blacklisted_token_family_fails(self):
        """
        Ensures that attempting to create a second BlacklistedTokenFamily
        for the same TokenFamily instance raises an IntegrityError or ValueError.
        """
        token_fam = TokenFamily.objects.create(
            user= self.user,
            family_id= uuid4().hex, 
            created_at= aware_utcnow(),
            expires_at= aware_utcnow() + timedelta(days=7), 
        )

        BlacklistedTokenFamily.objects.create(family=token_fam)

        with self.assertRaises((IntegrityError, ValueError)):
            BlacklistedTokenFamily.objects.create(family=token_fam)

    def test_family_delete_also_removes_the_blacklist_element(self):
        token_fam = TokenFamily.objects.create(
            user= self.user, 
            family_id= uuid4().hex,
            created_at= aware_utcnow(),
            expires_at= aware_utcnow() + timedelta(days=1), 
        )

        BlacklistedTokenFamily.objects.create(family= token_fam)

        self.assertEqual(BlacklistedTokenFamily.objects.all().count(), 1)

        token_fam.delete()

        self.assertEqual(TokenFamily.objects.all().count(), 0)
        self.assertEqual(BlacklistedTokenFamily.objects.all().count(), 0)


class TestTokenFamilyInRefreshTokens(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')

    def test_get_family_attributes_from_token(self):
        token = RefreshToken.for_user(self.user)

        self.assertIsNotNone(token.get_family_id())
        self.assertIsNotNone(token.get_family_expiration_date())

    def test_token_family_id_payload_value_must_be_a_string(self):
        token = RefreshToken.for_user(self.user)
        
        self.assertIsInstance(token[api_settings.TOKEN_FAMILY_CLAIM], str)
    
    def test_token_family_expiraton_payload_value_must_be_an_integer(self):
        token = RefreshToken.for_user(self.user)

        self.assertIsInstance(token[api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM], int)

    @override_api_settings(TOKEN_FAMILY_LIFETIME= None)
    def test_token_family_expiration_can_be_none(self):
        token = RefreshToken.for_user(self.user)

        self.assertIsNone(token.get_family_expiration_date())
        self.assertIsNone(token.get(api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM))
    
    def test_families_are_added_to_the_family_list(self):
        token = RefreshToken.for_user(self.user)
        qs = TokenFamily.objects.all()
        token_family_obj = qs.first()

        self.assertEqual(qs.count(), 1)
        self.assertEqual(token_family_obj.user, self.user)
        self.assertEqual(token_family_obj.family_id, token.get_family_id())
        self.assertEqual(token_family_obj.created_at, token.current_time)
        self.assertEqual(
            token_family_obj.expires_at.replace(microsecond=0), token.get_family_expiration_date().replace(microsecond=0)
            )
        
    def test_refresh_token_will_not_validate_if_family_is_blacklisted(self):
        token = RefreshToken.for_user(self.user)
        token_family_obj = TokenFamily.objects.first()

        # Should raise no exception
        RefreshToken(str(token))

        # Add family to blacklist
        BlacklistedTokenFamily.objects.create(family= token_family_obj)
        
        with self.assertRaises(TokenError) as cm:
            # Should raise exception
            RefreshToken(str(token))

        self.assertIn("family", cm.exception.args[0])
        self.assertIn("blacklisted", cm.exception.args[0])

    @override_api_settings(TOKEN_FAMILY_LIFETIME= timedelta(minutes= 30))
    def test_refresh_token_will_not_validate_if_family_is_expired(self):

        with freeze_time("2025-04-28 10:00:00"):
            token = RefreshToken.for_user(self.user)

        with freeze_time("2025-04-28 10:30:01"): # move time forward 30 mins + 1 sec
            with self.assertRaises(TokenError) as cm:
                RefreshToken(str(token))

            self.assertIn("family", cm.exception.args[0])
            self.assertIn("expired", cm.exception.args[0])

    def test_token_family_can_be_manually_blacklisted(self):
        token = RefreshToken.for_user(self.user)

         # Should raise no exception
        RefreshToken(str(token))

        self.assertEqual(TokenFamily.objects.count(), 1)

        # Add family to blacklist
        blacklisted_fam = token.blacklist_family()

        # Should not add family to tokenfamily list if already present
        self.assertEqual(TokenFamily.objects.count(), 1)

        # Should return blacklist record
        self.assertEqual(blacklisted_fam.family.family_id, token.get_family_id())

        with self.assertRaises(TokenError) as cm:
            # Should raise exception
            RefreshToken(str(token))
        
        self.assertIn("blacklisted", cm.exception.args[0])
        
        # This test checks that an error is raised when trying to blacklist a token
        # that does not have a family ID. Tokens created without the `for_user` 
        # method do not include family-related attributes, which are provided 
        # by the `FamilyMixin`. Since the token does not have a family, 
        # the `blacklist_family()` method should raise a `TokenError`.
        # 
        # Additionally, there is no point in creating a family to blacklist an 
        # isolated token, as the token is not part of any family, and creating 
        # a family for it will not affect the tokens that are related to it, 
        # since those other toknes will still have no family attribute.        
        new_token = RefreshToken()
        with self.assertRaises(TokenError) as cm:
            # Should raise exception
            new_token.blacklist_family()
        
        self.assertIn("no family", cm.exception.args[0])

        # Count should still be 1 since the previous token could not be added
        self.assertEqual(TokenFamily.objects.count(), 1)

    def test_family_attributes_do_not_change_for_new_tokens(self):
        token_1 = RefreshToken.for_user(self.user)

        # we genereate a new refresh token from token_1
        token_2 = RefreshToken(token= str(token_1))

        self.assertEqual(
            token_1[api_settings.TOKEN_FAMILY_CLAIM], token_2[api_settings.TOKEN_FAMILY_CLAIM]
            )
        self.assertEqual(
            token_1[api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM], token_2[api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM]
            )
    
    @override_api_settings(TOKEN_FAMILY_CLAIM= "fam_test_claim")
    def test_token_family_with_modify_family_claim(self):
        token = RefreshToken.for_user(self.user)

        self.assertEqual(api_settings.TOKEN_FAMILY_CLAIM, "fam_test_claim")
        self.assertIn("fam_test_claim", token.payload)

    @override_api_settings(TOKEN_FAMILY_EXPIRATION_CLAIM= "fam_test_exp_claim")
    def test_token_family_with_modify_family_expiration_claim(self):
        token = RefreshToken.for_user(self.user)

        self.assertEqual(api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM, "fam_test_exp_claim")
        self.assertIn("fam_test_exp_claim", token.payload)

    @override_api_settings(TOKEN_FAMILY_LIFETIME= timedelta(minutes= 30))
    def test_check_family_expiration_method(self):
        token: RefreshToken
        with freeze_time("2025-04-28 10:00:00"):
            token = RefreshToken.for_user(self.user)

        with freeze_time("2025-04-28 10:30:01"): # move time forward 30 mins + 1 sec
            with self.assertRaises(TokenError) as cm:
                # Call static method directly from the mixin
                FamilyMixin.check_family_expiration(token, aware_utcnow())
            
            self.assertIn("family", cm.exception.args[0])
            self.assertIn("expired", cm.exception.args[0])

            # Call via the instance (still a staticmethod, so same signature)
            with self.assertRaises(TokenError) as cm:
                token.check_family_expiration(token, aware_utcnow())
            
            self.assertIn("family", cm.exception.args[0])
            self.assertIn("expired", cm.exception.args[0])

    def test_family_blacklist_method(self):
        token = RefreshToken.for_user(self.user)
        token.blacklist_family()

        try:
            BlacklistedTokenFamily.objects.get(family__family_id = token.get_family_id())
        except BlacklistedTokenFamily.DoesNotExist:
            self.fail(
            f"Expected BlacklistedTokenFamily object with family_family_id='{token.get_family_id()}' "
            f"to exist after blacklisting the token, but it was not found in the database."
        )
     
    def test_check_family_blacklist_method(self):
        token = RefreshToken.for_user(self.user)
        token.blacklist_family()
        
        # Call static method directly from the mixin
        with self.assertRaises(TokenError) as cm:
            FamilyMixin.check_family_blacklist(token)
        
        self.assertIn("family", cm.exception.args[0])
        self.assertIn("blacklisted", cm.exception.args[0])

        # Call via the instance (still a staticmethod, so same signature)
        with self.assertRaises(TokenError) as cm:
            token.check_family_blacklist(token)
        
        self.assertIn("family", cm.exception.args[0])
        self.assertIn("blacklisted", cm.exception.args[0])

    def test_user_can_have_multiple_families(self):
        amount_of_tokens = 5
        tokens = [
            RefreshToken.for_user(self.user)
            for _ in range(amount_of_tokens)
        ]
        
        family_count = TokenFamily.objects.filter(user= self.user).count()
        self.assertEqual(family_count, amount_of_tokens)

    def test_family_id_uniqueness(self):
        """
        Tests that creating multiple separate tokens for the same user
        results in each token having a unique family id.
        """
        amount_of_tokens = 5
        families_ids = [
            RefreshToken.for_user(self.user).get_family_id()
            for _ in range(amount_of_tokens)
        ]

        # Converts the list of IDs to a set (which automatically removes duplicates)
        families_ids_set = set(families_ids)

        self.assertEqual(
            len(families_ids),
            len(families_ids_set),
            f"Expected {amount_of_tokens} unique family IDs, but found duplicates. IDs collected: {families_ids}"
        )

    def test_family_features_not_accessible_when_disabled(self):
        from rest_framework_simplejwt import tokens

        with override_api_settings(TOKEN_FAMILY_ENABLED= False):
            reload(tokens)
            token = tokens.RefreshToken.for_user(self.user)
        
            with self.assertRaises(AttributeError):
                token.get_family_id()

        # reloading to that the family mixin can have access to his methods
        with override_api_settings(TOKEN_FAMILY_ENABLED= True):
            reload(tokens)

class TestTokenFamilyInAccessTokens(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')

    @override_api_settings(TOKEN_FAMILY_CHECK_ON_ACCESS= True)
    def test_access_token_payload_can_include_family_claims(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token

        self.assertIn(api_settings.TOKEN_FAMILY_CLAIM, access.payload)
        self.assertIn(api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM, access.payload)

    @override_api_settings(TOKEN_FAMILY_CHECK_ON_ACCESS= False)
    def test_access_token_payload_can_exclude_family_claims(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token
        
        self.assertNotIn(api_settings.TOKEN_FAMILY_CLAIM, access.payload)
        self.assertNotIn(api_settings.TOKEN_FAMILY_EXPIRATION_CLAIM, access.payload)

    @override_api_settings(TOKEN_FAMILY_CHECK_ON_ACCESS= True)
    def test_access_token_will_not_validate_if_family_is_blacklisted(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token
        refresh.blacklist_family()

        with self.assertRaises(TokenError) as cm:
            AccessToken(str(access))

        self.assertIn("family", cm.exception.args[0])
        self.assertIn("blacklisted", cm.exception.args[0])

    @override_api_settings(
        TOKEN_FAMILY_CHECK_ON_ACCESS= True,
        TOKEN_FAMILY_LIFETIME= timedelta(minutes= 30),
        )
    def test_access_token_will_not_validate_if_family_is_expired(self):
        from rest_framework_simplejwt import tokens

        with override_api_settings(
            ACCESS_TOKEN_LIFETIME= timedelta(minutes=35),
        ):
            reload(tokens)

        with freeze_time("2025-04-28 10:00:00"):
            refresh = tokens.RefreshToken.for_user(self.user)
            access = refresh.access_token

        with freeze_time("2025-04-28 10:30:01"): # move time forward 30 mins + 1 sec
            with self.assertRaises(TokenError) as cm:
                tokens.AccessToken(str(access))

            self.assertIn("family", cm.exception.args[0])
            self.assertIn("expired", cm.exception.args[0])

        # relaod module back to default aceess lifetime
        with override_api_settings(
            ACCESS_TOKEN_LIFETIME= api_settings.ACCESS_TOKEN_LIFETIME,
        ):
            reload(tokens)

    @override_api_settings(TOKEN_FAMILY_CHECK_ON_ACCESS= True)         
    def test_access_token_verifies_family_blacklist(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token
        refresh.blacklist_family()

        with self.assertRaises(TokenError) as cm:
            access.verify()

        self.assertIn("family", cm.exception.args[0])
        self.assertIn("blacklisted", cm.exception.args[0])    
    
    @override_api_settings(
        TOKEN_FAMILY_CHECK_ON_ACCESS= True,
        TOKEN_FAMILY_LIFETIME= timedelta(minutes= 30)                
        )
    def test_access_token_varifies_family_expiration(self):
        access: AccessToken

        with freeze_time("2025-04-28 10:00:00"):
            refresh = RefreshToken.for_user(self.user)
            access = refresh.access_token

        with freeze_time("2025-04-28 10:30:01"): # move time forward 30 mins + 1 sec
            with self.assertRaises(TokenError) as cm:
                access.verify()

            self.assertIn("family", cm.exception.args[0])
            self.assertIn("expired", cm.exception.args[0])


class TestFlushExpiredTokenFamiliesCommand(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')

    @override_api_settings(TOKEN_FAMILY_LIFETIME= timedelta(minutes= 30))
    def test_it_should_delete_any_expire_families(self):
        amount_of_valid_families = 5
        amount_of_expired_families = 3
        amount_not_expired_blacklisted_families = 1
        amount_expired_blacklisted_families = 2

        valid_family_tokens: list[RefreshToken] = [
            RefreshToken.for_user(self.user)
            for _ in range(amount_of_valid_families)
        ]

        for i in range(amount_not_expired_blacklisted_families):
            valid_family_tokens[i].blacklist_family()

        expired_family_tokens: list[RefreshToken]
        with freeze_time(aware_utcnow() - timedelta(minutes=31)):
            expired_family_tokens = [
                RefreshToken.for_user(self.user)
                for _ in range(amount_of_expired_families)
            ]
            
        for i in range(amount_expired_blacklisted_families):
            expired_family_tokens[i].blacklist_family()

        self.assertEqual(
            TokenFamily.objects.all().count(),
            amount_of_expired_families + amount_of_valid_families            
        )
        self.assertEqual(
            BlacklistedTokenFamily.objects.all().count(),
            amount_expired_blacklisted_families + amount_not_expired_blacklisted_families
        )

        call_command("flushexpiredfamilies")

        self.assertEqual(
            TokenFamily.objects.all().count(),
            amount_of_valid_families            
        )
        self.assertEqual(
            BlacklistedTokenFamily.objects.all().count(),
            amount_not_expired_blacklisted_families
        )

    def test_family_will_not_remove_on_User_delete(self):
        token: RefreshToken = RefreshToken.for_user(self.user)
        token.blacklist_family()

        self.assertEqual(TokenFamily.objects.all().first().user, self.user)

        self.user.delete()

        self.assertEqual(TokenFamily.objects.all().count(), 1)
        self.assertEqual(BlacklistedTokenFamily.objects.all().count(), 1)
        self.assertIsNone(TokenFamily.objects.all().first().user)
        
    