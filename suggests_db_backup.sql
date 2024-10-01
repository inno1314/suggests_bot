--
-- PostgreSQL database dump
--

-- Dumped from database version 12.20 (Ubuntu 12.20-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.20 (Ubuntu 12.20-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ad_message; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.ad_message (
    id integer NOT NULL,
    html_text text NOT NULL,
    photo_link character varying(255),
    message_data json
);


ALTER TABLE public.ad_message OWNER TO inno;

--
-- Name: ad_message_id_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.ad_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ad_message_id_seq OWNER TO inno;

--
-- Name: ad_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.ad_message_id_seq OWNED BY public.ad_message.id;


--
-- Name: ad_message_views; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.ad_message_views (
    id integer NOT NULL,
    view_date date NOT NULL,
    view_count integer NOT NULL
);


ALTER TABLE public.ad_message_views OWNER TO inno;

--
-- Name: ad_message_views_id_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.ad_message_views_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ad_message_views_id_seq OWNER TO inno;

--
-- Name: ad_message_views_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.ad_message_views_id_seq OWNED BY public.ad_message_views.id;


--
-- Name: admin; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.admin (
    id bigint NOT NULL,
    language_code character varying(2) NOT NULL,
    name character varying(255),
    is_active boolean DEFAULT true NOT NULL,
    label character varying(255)
);


ALTER TABLE public.admin OWNER TO inno;

--
-- Name: admin_bot_association; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.admin_bot_association (
    admin_id bigint NOT NULL,
    bot_id bigint NOT NULL
);


ALTER TABLE public.admin_bot_association OWNER TO inno;

--
-- Name: admin_id_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.admin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_id_seq OWNER TO inno;

--
-- Name: admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.admin_id_seq OWNED BY public.admin.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO inno;

--
-- Name: bot; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.bot (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    url character varying(255) NOT NULL,
    language_code character varying(2) NOT NULL,
    banlist bigint[],
    sign_messages boolean DEFAULT true NOT NULL,
    post_formatting character varying(255),
    token character varying(255) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_premium boolean DEFAULT false NOT NULL,
    creator_id bigint NOT NULL
);


ALTER TABLE public.bot OWNER TO inno;

--
-- Name: bot_id_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.bot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bot_id_seq OWNER TO inno;

--
-- Name: bot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.bot_id_seq OWNED BY public.bot.id;


--
-- Name: channels; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.channels (
    primary_key bigint NOT NULL,
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    bot_id bigint
);


ALTER TABLE public.channels OWNER TO inno;

--
-- Name: channels_primary_key_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.channels_primary_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.channels_primary_key_seq OWNER TO inno;

--
-- Name: channels_primary_key_seq1; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.channels_primary_key_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.channels_primary_key_seq1 OWNER TO inno;

--
-- Name: channels_primary_key_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.channels_primary_key_seq1 OWNED BY public.channels.primary_key;


--
-- Name: invite_codes; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.invite_codes (
    code character varying(255) NOT NULL,
    bot_id bigint NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.invite_codes OWNER TO inno;

--
-- Name: mailing_message; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.mailing_message (
    id integer NOT NULL,
    html_text text NOT NULL,
    inline_text character varying(255) NOT NULL,
    inline_url character varying(255) NOT NULL,
    message_data json NOT NULL
);


ALTER TABLE public.mailing_message OWNER TO inno;

--
-- Name: mailing_message_id_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.mailing_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mailing_message_id_seq OWNER TO inno;

--
-- Name: mailing_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.mailing_message_id_seq OWNED BY public.mailing_message.id;


--
-- Name: sender; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.sender (
    id bigint NOT NULL,
    first_name character varying(255) NOT NULL,
    bot_id bigint,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.sender OWNER TO inno;

--
-- Name: sender_id_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.sender_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sender_id_seq OWNER TO inno;

--
-- Name: sender_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.sender_id_seq OWNED BY public.sender.id;


--
-- Name: sender_primary_key_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.sender_primary_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sender_primary_key_seq OWNER TO inno;

--
-- Name: subscription; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.subscription (
    id bigint NOT NULL,
    admin_id bigint NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    plan character varying(255) NOT NULL
);


ALTER TABLE public.subscription OWNER TO inno;

--
-- Name: subscription_id_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.subscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscription_id_seq OWNER TO inno;

--
-- Name: subscription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.subscription_id_seq OWNED BY public.subscription.id;


--
-- Name: suggested_message; Type: TABLE; Schema: public; Owner: inno
--

CREATE TABLE public.suggested_message (
    primary_key bigint NOT NULL,
    id bigint NOT NULL,
    chat_id bigint NOT NULL,
    media_group_id character varying(255) NOT NULL,
    group_id character varying(255) NOT NULL,
    sender_id bigint NOT NULL,
    bot_id bigint,
    html_text text NOT NULL,
    message_data json NOT NULL
);


ALTER TABLE public.suggested_message OWNER TO inno;

--
-- Name: suggested_message_primary_key_seq; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.suggested_message_primary_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.suggested_message_primary_key_seq OWNER TO inno;

--
-- Name: suggested_message_primary_key_seq1; Type: SEQUENCE; Schema: public; Owner: inno
--

CREATE SEQUENCE public.suggested_message_primary_key_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.suggested_message_primary_key_seq1 OWNER TO inno;

--
-- Name: suggested_message_primary_key_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: inno
--

ALTER SEQUENCE public.suggested_message_primary_key_seq1 OWNED BY public.suggested_message.primary_key;


--
-- Name: ad_message id; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.ad_message ALTER COLUMN id SET DEFAULT nextval('public.ad_message_id_seq'::regclass);


--
-- Name: ad_message_views id; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.ad_message_views ALTER COLUMN id SET DEFAULT nextval('public.ad_message_views_id_seq'::regclass);


--
-- Name: admin id; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.admin ALTER COLUMN id SET DEFAULT nextval('public.admin_id_seq'::regclass);


--
-- Name: bot id; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.bot ALTER COLUMN id SET DEFAULT nextval('public.bot_id_seq'::regclass);


--
-- Name: channels primary_key; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.channels ALTER COLUMN primary_key SET DEFAULT nextval('public.channels_primary_key_seq1'::regclass);


--
-- Name: mailing_message id; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.mailing_message ALTER COLUMN id SET DEFAULT nextval('public.mailing_message_id_seq'::regclass);


--
-- Name: sender id; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.sender ALTER COLUMN id SET DEFAULT nextval('public.sender_id_seq'::regclass);


--
-- Name: subscription id; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.subscription ALTER COLUMN id SET DEFAULT nextval('public.subscription_id_seq'::regclass);


--
-- Name: suggested_message primary_key; Type: DEFAULT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.suggested_message ALTER COLUMN primary_key SET DEFAULT nextval('public.suggested_message_primary_key_seq1'::regclass);


--
-- Data for Name: ad_message; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.ad_message (id, html_text, photo_link, message_data) FROM stdin;
\.


--
-- Data for Name: ad_message_views; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.ad_message_views (id, view_date, view_count) FROM stdin;
1	2024-08-30	3
2	2024-09-01	6
3	2024-09-02	1
\.


--
-- Data for Name: admin; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.admin (id, language_code, name, is_active, label) FROM stdin;
6435987938	ru	RT CODER [WORK]	t	None
5222370962	ru	Laptev	t	None
1461279208	ru	Логово Джеймса	t	None
5703157827	ru	RT MANAGER	t	None
5887319485	ru	SPOT	t	None
6690311726	ru	LH MANAGER [WORK]	t	None
5453810021	ru	Nik	t	None
1269500603	ru	ㅤ	t	None
1159890122	ru	Юра	t	None
575586402	ru	inno	t	None
5056637323	ru	ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ ㅤ	t	None
6733636191	ru	mytb♻️♻️♻️	t	None
402650044	ru	Greed	t	None
6173824087	ru	Виктория	t	None
440339950	ru	Денис	t	None
5911559164	ru	boklashka3008❂𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯𑲯	t	None
529640891	ru	Garik	t	None
1620039516	ru	Alf	t	None
5439494261	ru	Гриша	t	None
\.


--
-- Data for Name: admin_bot_association; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.admin_bot_association (admin_id, bot_id) FROM stdin;
5703157827	6397814703
5703157827	7472640565
5703157827	7480121104
5887319485	7472640565
6690311726	7480121104
5439494261	7538252901
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.alembic_version (version_num) FROM stdin;
0fa7871c5bcd
\.


--
-- Data for Name: bot; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.bot (id, name, url, language_code, banlist, sign_messages, post_formatting, token, is_active, is_premium, creator_id) FROM stdin;
6397814703	RT — Предложка	https://t.me/rt_subfeed_bot	ru	{}	t	\N	6397814703:AAFIb_O_m22Cn0mWRZkn24YMY6RT5d9Zvu4	t	t	5703157827
7472640565	SS — Предложка	https://t.me/ss_subfeed_bot	ru	{}	t	\N	7472640565:AAHKikeBBqasmjGnI1WA1QYaD6xnRLmhJtA	t	t	5703157827
7480121104	LH — Предложка	https://t.me/lh_subfeed_bot	ru	{}	t	\N	7480121104:AAHru5znrlWW1C9s82_De4r_mywApd8-_wE	t	f	5703157827
7538252901	TerkelFanBotPredlowka	https://t.me/TerkelFanBotPredlowkabot	ru	{}	t	\N	7538252901:AAEiYjKfreoBHqvxM2BB4vI-p9yswO1E6L4	t	f	5439494261
\.


--
-- Data for Name: channels; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.channels (primary_key, id, name, bot_id) FROM stdin;
\.


--
-- Data for Name: invite_codes; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.invite_codes (code, bot_id, is_active) FROM stdin;
\.


--
-- Data for Name: mailing_message; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.mailing_message (id, html_text, inline_text, inline_url, message_data) FROM stdin;
\.


--
-- Data for Name: sender; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.sender (id, first_name, bot_id, is_active) FROM stdin;
6945268089	testbot	\N	t
6690311726	LH MANAGER [WORK]	7480121104	t
1199430491	.	6397814703	f
5753748828	леха	6397814703	t
1628170846	𝓭𝓲𝓪𝓷𝓪	7472640565	t
5133749407	Noto	7480121104	t
1159890122	Юра	7480121104	t
6376194821	zuqtiis	6397814703	t
575586402	inno	6397814703	t
6824923444	Qavor_101💎	7480121104	t
207416885	Maria	6397814703	t
\.


--
-- Data for Name: subscription; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.subscription (id, admin_id, start_date, end_date, plan) FROM stdin;
1	5703157827	2024-08-30 12:02:28.114958+03	2025-08-31 20:06:23.106606+03	year
\.


--
-- Data for Name: suggested_message; Type: TABLE DATA; Schema: public; Owner: inno
--

COPY public.suggested_message (primary_key, id, chat_id, media_group_id, group_id, sender_id, bot_id, html_text, message_data) FROM stdin;
4	311	5703157827		cIXyvG8xcm	5753748828	6397814703	весь составчик	{"message_id": 310, "date": 1725139545, "chat": {"id": 5753748828, "type": "private", "title": null, "username": "Lut1zzz", "first_name": "\\u043b\\u0435\\u0445\\u0430", "last_name": null, "is_forum": null, "accent_color_id": null, "active_usernames": null, "available_reactions": null, "background_custom_emoji_id": null, "bio": null, "birthdate": null, "business_intro": null, "business_location": null, "business_opening_hours": null, "can_set_sticker_set": null, "custom_emoji_sticker_set_name": null, "description": null, "emoji_status_custom_emoji_id": null, "emoji_status_expiration_date": null, "has_aggressive_anti_spam_enabled": null, "has_hidden_members": null, "has_private_forwards": null, "has_protected_content": null, "has_restricted_voice_and_video_messages": null, "has_visible_history": null, "invite_link": null, "join_by_request": null, "join_to_send_messages": null, "linked_chat_id": null, "location": null, "message_auto_delete_time": null, "permissions": null, "personal_chat": null, "photo": null, "pinned_message": null, "profile_accent_color_id": null, "profile_background_custom_emoji_id": null, "slow_mode_delay": null, "sticker_set_name": null, "unrestrict_boost_count": null}, "message_thread_id": null, "from_user": {"id": 5753748828, "is_bot": false, "first_name": "\\u043b\\u0435\\u0445\\u0430", "last_name": null, "username": "Lut1zzz", "language_code": "ru", "is_premium": null, "added_to_attachment_menu": null, "can_join_groups": null, "can_read_all_group_messages": null, "supports_inline_queries": null, "can_connect_to_business": null}, "sender_chat": null, "sender_boost_count": null, "sender_business_bot": null, "business_connection_id": null, "forward_origin": null, "is_topic_message": null, "is_automatic_forward": null, "reply_to_message": null, "external_reply": null, "quote": null, "reply_to_story": null, "via_bot": null, "edit_date": null, "has_protected_content": null, "is_from_offline": null, "media_group_id": null, "author_signature": null, "text": null, "entities": null, "link_preview_options": null, "animation": null, "audio": null, "document": null, "photo": null, "sticker": null, "story": null, "video": {"file_id": "BAACAgIAAxkBAAIBNmbTild5oGVkTmp-euyVmUgz9mWeAAJsWAACP8mZSkOF3H4S7pSlNQQ", "file_unique_id": "AgADbFgAAj_JmUo", "width": 624, "height": 832, "duration": 38, "thumbnail": {"file_id": "AAMCAgADGQEAAgE2ZtOKV3mgZWROan567JWZSDP2ZZ4AAmxYAAI_yZlKQ4XcfhLulKUBAAdtAAM1BA", "file_unique_id": "AQADbFgAAj_JmUpy", "width": 240, "height": 320, "file_size": 13795}, "file_name": "IMG_6577.MOV", "mime_type": "video/mp4", "file_size": 31008949, "thumb": {"file_id": "AAMCAgADGQEAAgE2ZtOKV3mgZWROan567JWZSDP2ZZ4AAmxYAAI_yZlKQ4XcfhLulKUBAAdtAAM1BA", "file_unique_id": "AQADbFgAAj_JmUpy", "file_size": 13795, "width": 240, "height": 320}}, "video_note": null, "voice": null, "caption": "\\u0432\\u0435\\u0441\\u044c \\u0441\\u043e\\u0441\\u0442\\u0430\\u0432\\u0447\\u0438\\u043a", "caption_entities": null, "has_media_spoiler": null, "contact": null, "dice": null, "game": null, "poll": null, "venue": null, "location": null, "new_chat_members": null, "left_chat_member": null, "new_chat_title": null, "new_chat_photo": null, "delete_chat_photo": null, "group_chat_created": null, "supergroup_chat_created": null, "channel_chat_created": null, "message_auto_delete_timer_changed": null, "migrate_to_chat_id": null, "migrate_from_chat_id": null, "pinned_message": null, "invoice": null, "successful_payment": null, "users_shared": null, "chat_shared": null, "connected_website": null, "write_access_allowed": null, "passport_data": null, "proximity_alert_triggered": null, "boost_added": null, "chat_background_set": null, "forum_topic_created": null, "forum_topic_edited": null, "forum_topic_closed": null, "forum_topic_reopened": null, "general_forum_topic_hidden": null, "general_forum_topic_unhidden": null, "giveaway_created": null, "giveaway": null, "giveaway_winners": null, "giveaway_completed": null, "video_chat_scheduled": null, "video_chat_started": null, "video_chat_ended": null, "video_chat_participants_invited": null, "web_app_data": null, "reply_markup": null, "forward_date": null, "forward_from": null, "forward_from_chat": null, "forward_from_message_id": null, "forward_sender_name": null, "forward_signature": null, "user_shared": null}
5	314	5703157827		RS0yTejZH5	5753748828	6397814703	залет санька на конце	{"message_id": 313, "date": 1725139695, "chat": {"id": 5753748828, "type": "private", "title": null, "username": "Lut1zzz", "first_name": "\\u043b\\u0435\\u0445\\u0430", "last_name": null, "is_forum": null, "accent_color_id": null, "active_usernames": null, "available_reactions": null, "background_custom_emoji_id": null, "bio": null, "birthdate": null, "business_intro": null, "business_location": null, "business_opening_hours": null, "can_set_sticker_set": null, "custom_emoji_sticker_set_name": null, "description": null, "emoji_status_custom_emoji_id": null, "emoji_status_expiration_date": null, "has_aggressive_anti_spam_enabled": null, "has_hidden_members": null, "has_private_forwards": null, "has_protected_content": null, "has_restricted_voice_and_video_messages": null, "has_visible_history": null, "invite_link": null, "join_by_request": null, "join_to_send_messages": null, "linked_chat_id": null, "location": null, "message_auto_delete_time": null, "permissions": null, "personal_chat": null, "photo": null, "pinned_message": null, "profile_accent_color_id": null, "profile_background_custom_emoji_id": null, "slow_mode_delay": null, "sticker_set_name": null, "unrestrict_boost_count": null}, "message_thread_id": null, "from_user": {"id": 5753748828, "is_bot": false, "first_name": "\\u043b\\u0435\\u0445\\u0430", "last_name": null, "username": "Lut1zzz", "language_code": "ru", "is_premium": null, "added_to_attachment_menu": null, "can_join_groups": null, "can_read_all_group_messages": null, "supports_inline_queries": null, "can_connect_to_business": null}, "sender_chat": null, "sender_boost_count": null, "sender_business_bot": null, "business_connection_id": null, "forward_origin": null, "is_topic_message": null, "is_automatic_forward": null, "reply_to_message": null, "external_reply": null, "quote": null, "reply_to_story": null, "via_bot": null, "edit_date": null, "has_protected_content": null, "is_from_offline": null, "media_group_id": null, "author_signature": null, "text": null, "entities": null, "link_preview_options": null, "animation": null, "audio": null, "document": null, "photo": null, "sticker": null, "story": null, "video": {"file_id": "BAACAgIAAxkBAAIBOWbTiu8XCpBF4oqiETtGcDzRLRCSAAJxWAACP8mZStNaS-rQHwdINQQ", "file_unique_id": "AgADcVgAAj_JmUo", "width": 1920, "height": 1074, "duration": 23, "thumbnail": {"file_id": "AAMCAgADGQEAAgE5ZtOK7xcKkEXiiqIRO0ZwPNEtEJIAAnFYAAI_yZlK01pL6tAfB0gBAAdtAAM1BA", "file_unique_id": "AQADcVgAAj_JmUpy", "width": 320, "height": 179, "file_size": 13084}, "file_name": "IMG_6566.MOV", "mime_type": "video/mp4", "file_size": 18922091, "thumb": {"file_id": "AAMCAgADGQEAAgE5ZtOK7xcKkEXiiqIRO0ZwPNEtEJIAAnFYAAI_yZlK01pL6tAfB0gBAAdtAAM1BA", "file_unique_id": "AQADcVgAAj_JmUpy", "file_size": 13084, "width": 320, "height": 179}}, "video_note": null, "voice": null, "caption": "\\u0437\\u0430\\u043b\\u0435\\u0442 \\u0441\\u0430\\u043d\\u044c\\u043a\\u0430 \\u043d\\u0430 \\u043a\\u043e\\u043d\\u0446\\u0435", "caption_entities": null, "has_media_spoiler": null, "contact": null, "dice": null, "game": null, "poll": null, "venue": null, "location": null, "new_chat_members": null, "left_chat_member": null, "new_chat_title": null, "new_chat_photo": null, "delete_chat_photo": null, "group_chat_created": null, "supergroup_chat_created": null, "channel_chat_created": null, "message_auto_delete_timer_changed": null, "migrate_to_chat_id": null, "migrate_from_chat_id": null, "pinned_message": null, "invoice": null, "successful_payment": null, "users_shared": null, "chat_shared": null, "connected_website": null, "write_access_allowed": null, "passport_data": null, "proximity_alert_triggered": null, "boost_added": null, "chat_background_set": null, "forum_topic_created": null, "forum_topic_edited": null, "forum_topic_closed": null, "forum_topic_reopened": null, "general_forum_topic_hidden": null, "general_forum_topic_unhidden": null, "giveaway_created": null, "giveaway": null, "giveaway_winners": null, "giveaway_completed": null, "video_chat_scheduled": null, "video_chat_started": null, "video_chat_ended": null, "video_chat_participants_invited": null, "web_app_data": null, "reply_markup": null, "forward_date": null, "forward_from": null, "forward_from_chat": null, "forward_from_message_id": null, "forward_sender_name": null, "forward_signature": null, "user_shared": null}
6	317	5703157827		31wapMCy5r	5753748828	6397814703		{"message_id": 316, "date": 1725140097, "chat": {"id": 5753748828, "type": "private", "title": null, "username": "Lut1zzz", "first_name": "\\u043b\\u0435\\u0445\\u0430", "last_name": null, "is_forum": null, "accent_color_id": null, "active_usernames": null, "available_reactions": null, "background_custom_emoji_id": null, "bio": null, "birthdate": null, "business_intro": null, "business_location": null, "business_opening_hours": null, "can_set_sticker_set": null, "custom_emoji_sticker_set_name": null, "description": null, "emoji_status_custom_emoji_id": null, "emoji_status_expiration_date": null, "has_aggressive_anti_spam_enabled": null, "has_hidden_members": null, "has_private_forwards": null, "has_protected_content": null, "has_restricted_voice_and_video_messages": null, "has_visible_history": null, "invite_link": null, "join_by_request": null, "join_to_send_messages": null, "linked_chat_id": null, "location": null, "message_auto_delete_time": null, "permissions": null, "personal_chat": null, "photo": null, "pinned_message": null, "profile_accent_color_id": null, "profile_background_custom_emoji_id": null, "slow_mode_delay": null, "sticker_set_name": null, "unrestrict_boost_count": null}, "message_thread_id": null, "from_user": {"id": 5753748828, "is_bot": false, "first_name": "\\u043b\\u0435\\u0445\\u0430", "last_name": null, "username": "Lut1zzz", "language_code": "ru", "is_premium": null, "added_to_attachment_menu": null, "can_join_groups": null, "can_read_all_group_messages": null, "supports_inline_queries": null, "can_connect_to_business": null}, "sender_chat": null, "sender_boost_count": null, "sender_business_bot": null, "business_connection_id": null, "forward_origin": null, "is_topic_message": null, "is_automatic_forward": null, "reply_to_message": null, "external_reply": null, "quote": null, "reply_to_story": null, "via_bot": null, "edit_date": null, "has_protected_content": null, "is_from_offline": null, "media_group_id": null, "author_signature": null, "text": null, "entities": null, "link_preview_options": null, "animation": null, "audio": null, "document": null, "photo": null, "sticker": null, "story": null, "video": {"file_id": "BAACAgIAAxkBAAIBPGbTjIGE7UGzUxo_4toGAXrSIHDsAAKAWAACP8mZSvhGMmp3azJANQQ", "file_unique_id": "AgADgFgAAj_JmUo", "width": 1072, "height": 1920, "duration": 11, "thumbnail": {"file_id": "AAMCAgADGQEAAgE8ZtOMgYTtQbNTGj_i2gYBetIgcOwAAoBYAAI_yZlK-EYyandrMkABAAdtAAM1BA", "file_unique_id": "AQADgFgAAj_JmUpy", "width": 179, "height": 320, "file_size": 8536}, "file_name": "IMG_6529.MOV", "mime_type": "video/mp4", "file_size": 8531660, "thumb": {"file_id": "AAMCAgADGQEAAgE8ZtOMgYTtQbNTGj_i2gYBetIgcOwAAoBYAAI_yZlK-EYyandrMkABAAdtAAM1BA", "file_unique_id": "AQADgFgAAj_JmUpy", "file_size": 8536, "width": 179, "height": 320}}, "video_note": null, "voice": null, "caption": null, "caption_entities": null, "has_media_spoiler": null, "contact": null, "dice": null, "game": null, "poll": null, "venue": null, "location": null, "new_chat_members": null, "left_chat_member": null, "new_chat_title": null, "new_chat_photo": null, "delete_chat_photo": null, "group_chat_created": null, "supergroup_chat_created": null, "channel_chat_created": null, "message_auto_delete_timer_changed": null, "migrate_to_chat_id": null, "migrate_from_chat_id": null, "pinned_message": null, "invoice": null, "successful_payment": null, "users_shared": null, "chat_shared": null, "connected_website": null, "write_access_allowed": null, "passport_data": null, "proximity_alert_triggered": null, "boost_added": null, "chat_background_set": null, "forum_topic_created": null, "forum_topic_edited": null, "forum_topic_closed": null, "forum_topic_reopened": null, "general_forum_topic_hidden": null, "general_forum_topic_unhidden": null, "giveaway_created": null, "giveaway": null, "giveaway_winners": null, "giveaway_completed": null, "video_chat_scheduled": null, "video_chat_started": null, "video_chat_ended": null, "video_chat_participants_invited": null, "web_app_data": null, "reply_markup": null, "forward_date": null, "forward_from": null, "forward_from_chat": null, "forward_from_message_id": null, "forward_sender_name": null, "forward_signature": null, "user_shared": null}
13	326	5703157827		Uts3N0PFOz	207416885	6397814703	Добрый день!\nМеня зовут Мария, я продюсер подкаста "Творческая личность" - это подкаст о том, как заниматься творческой деятельностью и зарабатывать ей деньги.\n\nСегодня у нас вышел эпизод, героем которого стал поэт и рэп-артист Наум Блик,  которого «Википедия» называет предтечей екатеринбургского хип-хопа. \n\nСейчас Наум живет во Франции. Там он работает на простой работе, учит язык, ходит по выставкам и продолжает писать стихи, что бы ни происходило вокруг. Мы поговорили с Наумом о том, как после 40 начать с нуля в новой стране, сколько нужно денег, чтобы выжить в Париже и о многом другом.\n\nПодскажите, пожалуйста, было бы вам интересно поделиться с читателями тг-канала ссылкой на эпизод подкаста? Есть ли у вас такая опция?🙂\nМы в благодарность можем рассказать о вас в нашем небольшом телеграм-канале. \n\nСсылка на эпизод: https://podcast.ru/e/1QTpn~FRgC6\nНаш тг канал: https://t.me/creativepersonpodcast	{"message_id": 325, "date": "1725258864", "chat": {"id": 207416885, "type": "private", "username": "ov_maria", "first_name": "Maria", "last_name": "Ovsyannikova"}, "from_user": {"id": 207416885, "is_bot": false, "first_name": "Maria", "last_name": "Ovsyannikova", "username": "ov_maria", "language_code": "ru"}, "text": "\\u0414\\u043e\\u0431\\u0440\\u044b\\u0439 \\u0434\\u0435\\u043d\\u044c!\\n\\u041c\\u0435\\u043d\\u044f \\u0437\\u043e\\u0432\\u0443\\u0442 \\u041c\\u0430\\u0440\\u0438\\u044f, \\u044f \\u043f\\u0440\\u043e\\u0434\\u044e\\u0441\\u0435\\u0440 \\u043f\\u043e\\u0434\\u043a\\u0430\\u0441\\u0442\\u0430 \\"\\u0422\\u0432\\u043e\\u0440\\u0447\\u0435\\u0441\\u043a\\u0430\\u044f \\u043b\\u0438\\u0447\\u043d\\u043e\\u0441\\u0442\\u044c\\" - \\u044d\\u0442\\u043e \\u043f\\u043e\\u0434\\u043a\\u0430\\u0441\\u0442 \\u043e \\u0442\\u043e\\u043c, \\u043a\\u0430\\u043a \\u0437\\u0430\\u043d\\u0438\\u043c\\u0430\\u0442\\u044c\\u0441\\u044f \\u0442\\u0432\\u043e\\u0440\\u0447\\u0435\\u0441\\u043a\\u043e\\u0439 \\u0434\\u0435\\u044f\\u0442\\u0435\\u043b\\u044c\\u043d\\u043e\\u0441\\u0442\\u044c\\u044e \\u0438 \\u0437\\u0430\\u0440\\u0430\\u0431\\u0430\\u0442\\u044b\\u0432\\u0430\\u0442\\u044c \\u0435\\u0439 \\u0434\\u0435\\u043d\\u044c\\u0433\\u0438.\\n\\n\\u0421\\u0435\\u0433\\u043e\\u0434\\u043d\\u044f \\u0443 \\u043d\\u0430\\u0441 \\u0432\\u044b\\u0448\\u0435\\u043b \\u044d\\u043f\\u0438\\u0437\\u043e\\u0434, \\u0433\\u0435\\u0440\\u043e\\u0435\\u043c \\u043a\\u043e\\u0442\\u043e\\u0440\\u043e\\u0433\\u043e \\u0441\\u0442\\u0430\\u043b \\u043f\\u043e\\u044d\\u0442 \\u0438 \\u0440\\u044d\\u043f-\\u0430\\u0440\\u0442\\u0438\\u0441\\u0442 \\u041d\\u0430\\u0443\\u043c \\u0411\\u043b\\u0438\\u043a,  \\u043a\\u043e\\u0442\\u043e\\u0440\\u043e\\u0433\\u043e \\u00ab\\u0412\\u0438\\u043a\\u0438\\u043f\\u0435\\u0434\\u0438\\u044f\\u00bb \\u043d\\u0430\\u0437\\u044b\\u0432\\u0430\\u0435\\u0442 \\u043f\\u0440\\u0435\\u0434\\u0442\\u0435\\u0447\\u0435\\u0439 \\u0435\\u043a\\u0430\\u0442\\u0435\\u0440\\u0438\\u043d\\u0431\\u0443\\u0440\\u0433\\u0441\\u043a\\u043e\\u0433\\u043e \\u0445\\u0438\\u043f-\\u0445\\u043e\\u043f\\u0430. \\n\\n\\u0421\\u0435\\u0439\\u0447\\u0430\\u0441 \\u041d\\u0430\\u0443\\u043c \\u0436\\u0438\\u0432\\u0435\\u0442 \\u0432\\u043e \\u0424\\u0440\\u0430\\u043d\\u0446\\u0438\\u0438. \\u0422\\u0430\\u043c \\u043e\\u043d \\u0440\\u0430\\u0431\\u043e\\u0442\\u0430\\u0435\\u0442 \\u043d\\u0430 \\u043f\\u0440\\u043e\\u0441\\u0442\\u043e\\u0439 \\u0440\\u0430\\u0431\\u043e\\u0442\\u0435, \\u0443\\u0447\\u0438\\u0442 \\u044f\\u0437\\u044b\\u043a, \\u0445\\u043e\\u0434\\u0438\\u0442 \\u043f\\u043e \\u0432\\u044b\\u0441\\u0442\\u0430\\u0432\\u043a\\u0430\\u043c \\u0438 \\u043f\\u0440\\u043e\\u0434\\u043e\\u043b\\u0436\\u0430\\u0435\\u0442 \\u043f\\u0438\\u0441\\u0430\\u0442\\u044c \\u0441\\u0442\\u0438\\u0445\\u0438, \\u0447\\u0442\\u043e \\u0431\\u044b \\u043d\\u0438 \\u043f\\u0440\\u043e\\u0438\\u0441\\u0445\\u043e\\u0434\\u0438\\u043b\\u043e \\u0432\\u043e\\u043a\\u0440\\u0443\\u0433. \\u041c\\u044b \\u043f\\u043e\\u0433\\u043e\\u0432\\u043e\\u0440\\u0438\\u043b\\u0438 \\u0441 \\u041d\\u0430\\u0443\\u043c\\u043e\\u043c \\u043e \\u0442\\u043e\\u043c, \\u043a\\u0430\\u043a \\u043f\\u043e\\u0441\\u043b\\u0435 40 \\u043d\\u0430\\u0447\\u0430\\u0442\\u044c \\u0441 \\u043d\\u0443\\u043b\\u044f \\u0432 \\u043d\\u043e\\u0432\\u043e\\u0439 \\u0441\\u0442\\u0440\\u0430\\u043d\\u0435, \\u0441\\u043a\\u043e\\u043b\\u044c\\u043a\\u043e \\u043d\\u0443\\u0436\\u043d\\u043e \\u0434\\u0435\\u043d\\u0435\\u0433, \\u0447\\u0442\\u043e\\u0431\\u044b \\u0432\\u044b\\u0436\\u0438\\u0442\\u044c \\u0432 \\u041f\\u0430\\u0440\\u0438\\u0436\\u0435 \\u0438 \\u043e \\u043c\\u043d\\u043e\\u0433\\u043e\\u043c \\u0434\\u0440\\u0443\\u0433\\u043e\\u043c.\\n\\n\\u041f\\u043e\\u0434\\u0441\\u043a\\u0430\\u0436\\u0438\\u0442\\u0435, \\u043f\\u043e\\u0436\\u0430\\u043b\\u0443\\u0439\\u0441\\u0442\\u0430, \\u0431\\u044b\\u043b\\u043e \\u0431\\u044b \\u0432\\u0430\\u043c \\u0438\\u043d\\u0442\\u0435\\u0440\\u0435\\u0441\\u043d\\u043e \\u043f\\u043e\\u0434\\u0435\\u043b\\u0438\\u0442\\u044c\\u0441\\u044f \\u0441 \\u0447\\u0438\\u0442\\u0430\\u0442\\u0435\\u043b\\u044f\\u043c\\u0438 \\u0442\\u0433-\\u043a\\u0430\\u043d\\u0430\\u043b\\u0430 \\u0441\\u0441\\u044b\\u043b\\u043a\\u043e\\u0439 \\u043d\\u0430 \\u044d\\u043f\\u0438\\u0437\\u043e\\u0434 \\u043f\\u043e\\u0434\\u043a\\u0430\\u0441\\u0442\\u0430? \\u0415\\u0441\\u0442\\u044c \\u043b\\u0438 \\u0443 \\u0432\\u0430\\u0441 \\u0442\\u0430\\u043a\\u0430\\u044f \\u043e\\u043f\\u0446\\u0438\\u044f?\\ud83d\\ude42\\n\\u041c\\u044b \\u0432 \\u0431\\u043b\\u0430\\u0433\\u043e\\u0434\\u0430\\u0440\\u043d\\u043e\\u0441\\u0442\\u044c \\u043c\\u043e\\u0436\\u0435\\u043c \\u0440\\u0430\\u0441\\u0441\\u043a\\u0430\\u0437\\u0430\\u0442\\u044c \\u043e \\u0432\\u0430\\u0441 \\u0432 \\u043d\\u0430\\u0448\\u0435\\u043c \\u043d\\u0435\\u0431\\u043e\\u043b\\u044c\\u0448\\u043e\\u043c \\u0442\\u0435\\u043b\\u0435\\u0433\\u0440\\u0430\\u043c-\\u043a\\u0430\\u043d\\u0430\\u043b\\u0435. \\n\\n\\u0421\\u0441\\u044b\\u043b\\u043a\\u0430 \\u043d\\u0430 \\u044d\\u043f\\u0438\\u0437\\u043e\\u0434: https://podcast.ru/e/1QTpn~FRgC6\\n\\u041d\\u0430\\u0448 \\u0442\\u0433 \\u043a\\u0430\\u043d\\u0430\\u043b: https://t.me/creativepersonpodcast", "entities": [{"type": "url", "offset": 832, "length": 32}, {"type": "url", "offset": 879, "length": 34}], "link_preview_options": {"url": "https://podcast.ru/e/1QTpn~FRgC6"}}
\.


--
-- Name: ad_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.ad_message_id_seq', 1, false);


--
-- Name: ad_message_views_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.ad_message_views_id_seq', 3, true);


--
-- Name: admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.admin_id_seq', 1, false);


--
-- Name: bot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.bot_id_seq', 1, false);


--
-- Name: channels_primary_key_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.channels_primary_key_seq', 5, true);


--
-- Name: channels_primary_key_seq1; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.channels_primary_key_seq1', 1, false);


--
-- Name: mailing_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.mailing_message_id_seq', 1, false);


--
-- Name: sender_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.sender_id_seq', 1, false);


--
-- Name: sender_primary_key_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.sender_primary_key_seq', 3, true);


--
-- Name: subscription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.subscription_id_seq', 1, true);


--
-- Name: suggested_message_primary_key_seq; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.suggested_message_primary_key_seq', 32, true);


--
-- Name: suggested_message_primary_key_seq1; Type: SEQUENCE SET; Schema: public; Owner: inno
--

SELECT pg_catalog.setval('public.suggested_message_primary_key_seq1', 13, true);


--
-- Name: ad_message ad_message_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.ad_message
    ADD CONSTRAINT ad_message_pkey PRIMARY KEY (id);


--
-- Name: ad_message_views ad_message_views_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.ad_message_views
    ADD CONSTRAINT ad_message_views_pkey PRIMARY KEY (id);


--
-- Name: admin_bot_association admin_bot_association_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.admin_bot_association
    ADD CONSTRAINT admin_bot_association_pkey PRIMARY KEY (admin_id, bot_id);


--
-- Name: admin admin_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bot bot_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.bot
    ADD CONSTRAINT bot_pkey PRIMARY KEY (id);


--
-- Name: bot bot_token_key; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.bot
    ADD CONSTRAINT bot_token_key UNIQUE (token);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (primary_key);


--
-- Name: invite_codes invite_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.invite_codes
    ADD CONSTRAINT invite_codes_pkey PRIMARY KEY (code);


--
-- Name: mailing_message mailing_message_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.mailing_message
    ADD CONSTRAINT mailing_message_pkey PRIMARY KEY (id);


--
-- Name: sender sender_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.sender
    ADD CONSTRAINT sender_pkey PRIMARY KEY (id);


--
-- Name: subscription subscription_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.subscription
    ADD CONSTRAINT subscription_pkey PRIMARY KEY (id);


--
-- Name: suggested_message suggested_message_pkey; Type: CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.suggested_message
    ADD CONSTRAINT suggested_message_pkey PRIMARY KEY (primary_key);


--
-- Name: admin_bot_association admin_bot_association_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.admin_bot_association
    ADD CONSTRAINT admin_bot_association_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.admin(id);


--
-- Name: admin_bot_association admin_bot_association_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.admin_bot_association
    ADD CONSTRAINT admin_bot_association_bot_id_fkey FOREIGN KEY (bot_id) REFERENCES public.bot(id);


--
-- Name: bot bot_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.bot
    ADD CONSTRAINT bot_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.admin(id);


--
-- Name: channels channels_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_bot_id_fkey FOREIGN KEY (bot_id) REFERENCES public.bot(id);


--
-- Name: sender sender_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.sender
    ADD CONSTRAINT sender_bot_id_fkey FOREIGN KEY (bot_id) REFERENCES public.bot(id) ON DELETE SET NULL;


--
-- Name: subscription subscription_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.subscription
    ADD CONSTRAINT subscription_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.admin(id);


--
-- Name: suggested_message suggested_message_bot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.suggested_message
    ADD CONSTRAINT suggested_message_bot_id_fkey FOREIGN KEY (bot_id) REFERENCES public.bot(id);


--
-- Name: suggested_message suggested_message_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inno
--

ALTER TABLE ONLY public.suggested_message
    ADD CONSTRAINT suggested_message_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.sender(id);


--
-- PostgreSQL database dump complete
--

